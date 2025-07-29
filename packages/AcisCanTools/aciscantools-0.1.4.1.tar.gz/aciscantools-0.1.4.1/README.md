# AcisCanTools

AcisCanTools is a Python toolkit for logging, parsing, simulating, and analyzing CAN (Controller Area Network) data, with a focus on emissions sensor data such as NO<sub>x</sub> and O₂ using the [PythonCAN](https://python-can.readthedocs.io/en/stable/api.html) module in the background. It provides utilities for working with raw CAN logs, parsing sensor data, and for simulating CAN traffic for testing and development.

---

## Features

- **Logger**: Log CAN traffic's arbitration information and raw data to CSV or JSON, or use as a datastream.
- **Parser**: Extends the logger class, has specific functionality for parsing NOx sensor data when generating logs
- **PandaStream**: Behaves similarly to the `Logger` object in datastream mode. Rather that collecting `can.Packet` objects though, it creates instances of the `pandas.Series` object, containing Source, NOx, and O2 information to be used a column in real-time dataframes
- **sensorSim**: An object that allows you to exactly re-create a CAN data source's output in real time given a CSV log generated from this package
- **CanVis**: A static class built on top of Pandas and Matplotlib that gives various ways to seamlessly visualize logs as well as their dataframe representations. (Pronounced 'canvis' becase I thought it was clever, idk)
- **Utils**: A class containing various static methods for handling and processing CAN data

---

## Installation

The latest release of the AcisCanTools package can be installed from PyPi through pip, using `pip install AcisCanTools` or some equivalent to install into your specific environment

---

## Usage

### Logging CAN Data

```python
from AcisCanTools import Logger

# Log CAN data from interface 'can0' to a CSV file
# Records arbitration information and raw hex data
logger = Logger(interface='can0', output_file='log.csv')
try:
    logger.run_csv_logging()
except KeyboardInterrupt:
    print("\n")
    logger.bus.shutdown()
    print("Replay stopped by user.")
"""
Output format:
No., Time, Snd/Rc, Dest, Src, Priority, PGN, Data
"""
```

### Logging Sensor-Specific Data

```python
from AcisCanTools import Parser

# Log CAN data from interface 'can0' to a CSV file
# Records arbitration information and attempts to parse data section
logger = Parser(interface='can0', output_file='log.csv')
logger.configure_smart_nox_output()
try:
    logger.run_csv_logging()
except KeyboardInterrupt:
    print("\n")
    logger.bus.shutdown()
    print("Replay stopped by user.")
"""
Output format:
No., Time, Snd/Rc, Dest, Src, Priority, PGN, NOx Raw, O2 Raw, Status, Heater, Error NOx, Error O2
"""
```

>Context: In the above example, the calling of `configure_smart_nox_output()` does two things, it firstly allows the user to determine which data they want out, if you wish to exclude a datafield you can pass that field as a False argument, if I wished to only receive raw NO<sub>x</sub> and O<sub>2</sub> I would run the following before beginning logging:

```python
configure_smart_nox_output(status=False, heater=False, error_nox=False, error_o2=False)
```

In addition, calling this function also sets an internal flag telling the Parser class to interpret the data as specified in the datasheet for the Continental Smart NO<sub>x</sub> Sensor.
Currently, this is the only data format supported by the Parser object, and this format is implied if not specified, but it is setup in such a way that a hypothetical `configure_for_some_other_device()` method could be added, and implemented directly into the parser class with relative ease for future development and utility.

### Reading CAN Traffic

if you wish to simply read data, this can also be acheived with the Logger class
> Note: this is essentially just a wrapper for the PythonCAN module, do with that information as you wish

The Parser class does not contain an overload for the Logger's `read()` method as there are multiple ways to more freely handle the parsed data available in the `utils` class

```python
from AcisCanTools import Logger

log = Logger(interface="can0", mode="stream") # Create a logger object in datastream mode

while True:
    try:
        # None value is returned after specified period iff argument is provided
        packet = log.read(timeout=1)
        print(packet)
    except KeyboardInterrupt:
        print("\n")
        log.bus.shutdown()
        print("Replay stopped by user.")
        break
```

In comparison to `Logger`, the `PandaStream` object operates exclusively in the datastream mode so instantiation is slightly different but otherwise the two are largely interchangeable.

```python
from AcisCanTools import Logger

log = PandaStream(interface="can0")

while True:
    try:
        # None value is returned after specified period iff argument is provided
        packet = log.read(timeout=1)
        print(packet)
        # Packet is a pandas.Series object of length 4, indexed as [NOx Raw, O2 Raw, Src, PGN]
    except KeyboardInterrupt:
        print("\n")
        log.bus.shutdown()
        print("Replay stopped by user.")
        break
```

### Static Decoding

When given the data attribute of a `can.Message` object (or really any acceptably formatted bytearray), returns a tuple containing parsed/decoded values.
Also accepts an argument for the device type, currently only supports the smart nox sensor and defaults to it
For smart_nox, the output is formatted as
`(nox_raw, o2_raw, status, heater, error_nox, error_o2)`

```python
import AcisCanTools as ACT

log = ACT.Logger(interface='can0', mode='stream')
packet = log.read()
print(ACT.utils.static_decode(packet.data))
```

### Converting Raw NO<sub>x</sub> and O<sub>2</sub> Values

The utils class contains two methods to statically convert the raw NO<sub>x</sub> and O<sub>2</sub> values sent by the NO<sub>x</sub> sensor to meaningful unit-values using the following conversion factors

<div style="display: flex; justify-content: space-evenly; align-items: center; gap: 20px;">
  <img src="assets/NOx_Equation.png" alt="NOx Conversion Equation" width="300"/>
  <img src="assets/O2_Equation.png" alt="O2 Conversion Equation" width="300"/>
</div>

These functions can be called on a singlular value or mapped across an array

```python
import AcisCanTools as ACT

log = ACT.Logger(interface="can0", mode="stream")
data = ACT.static_decode(log.read().data)

# Note: data[0] and data[1] are the raw NOx and O2 values respectively
print(f"NOx: {act.utils.convert_NOx(data[0])}PPM")
print(f"O2: {act.utils.convert_O2(data[1])}%")
```

### Isolating Arbirtation and Payload Information

The utils class contains two methods to selectively extract specific fields from raw CAN information. For arbitration data, bit shifting and masking is required to get meaningful information out of an ID, this method performs this task for a specified field, as when reading the data live we often don't need every peice of information. Likewise, there is a sister method for extracting data payloads for NO<sub>x</sub> sensor data, this method is also able to perform the raw to real conversion for NO<sub>x</sub> and O<sub>2</sub>.

```python
import AcisCanTools as ACT
from AcisCanTools import utils as u

log = ACT.Logger(mode="stream", interface=u.get_can_interface())
packet = log.read(timeout=1)
if packet is not None:
    pgn = u.extract_arbitration_field(packet.arbitration_id, 'pgn') # PGN value
    nox = u.extract_data_field(packet.data, 'nox', convert_raw=True) # Converted NOx value
```

Note that in versions `0.1.3` and later there are some additional data isolation and management methods built on top of Pandas dataframes that will prove more useful in execution. The primary benifit of the Pandas methods being a much more seamless transition between CSV logs and DataFrame objects.

### Hardware Detection and Checking

The utils class also contains two methods for detecting a CAN interface on your system as well as checking the status of your primary interface if it exists
>⚠️ Warning: These methods function by running variants of the `ip link` command found on the vast majority of linux systems, as a result, you will not get the desired output on a Windows or Mac system.

#### Checking Hardware

The `get_can_interface` function attempts to detect a can interface on your device, by default it assumes you have a single interface, or at least use to use the first one in your network settings, and will return only the name of the interface, which can be used as an argument when instantiating the Logger class. The function can also be ran with `verbose=True`, which will instead return the full output of `ip link show type can`, useful for debugging.

```python
import AcisCanTools as ACT

interface = ACT.utils.get_can_interface() # likely "can0" or similar if sucessful

example = Logger(interface=ACT.utils.get_can_interface()) # Also works
```

#### Verifying Interface

In addition to pulling the name of an interface, there is anther method for checking the UP/DOWN status of your first/primary interface, it can be a troubleshooting tool if you are unable to pull data off of an interface
In the instance that your adapter is shown as down, a good next step is running
`sudo ip link set {adapter name} up` in your terminal

```python
import AcisCanTools as ACT

print(ACT.utils.check_can_status() # either "UP" or "DOWN"
```

### Simulating CAN Traffic

This package also contains the ability to emulate a can datasource based off of a CSV file generated from the Logger or Parser classes. The object uses the timestamps in the log to recreate the data source as accurately as possible; the class is capable of sending CAN data in such a way that when logged is exaxtly identical to the input file.

If you do with to send and collect/log data on the same device, the easiest way it to set your interface to loopback mode, which will basically let you send packets to yourself, it will also prevent you from receiving data from outside sources so remember to turn it off before you read from a real data source. On a linux system you can temporarily enable loopback mode in the terminal by running:

```bash
sudo ip link set {interface} down
sudo ip link set {interface} type can loopback on
sudo ip link set {interface} up
```

you can disable loopback by doing the exact same thing, replacing `on` with `off` at the end of the second command, or by rebooting your system

When using loopback mode and receiving packets, you will see that you end up receiving two copies of every packet, one received normally, and one echoed by your system. When logging, this results in logs exactly twice as long as the input logs, with two of each packet, to fix this, you can pass `loopback=True` as an argument when calling the logger or Parser. When collecting data using the `read()` function, you will have to deal with these duplicate packets yourself but you can just skip every other one with very little risk of accidentally losing data. Additionally you can also try disabling the echo when setting your adapter to loopback mode. There is also a dataFormat argument, dictating if the provided log is generated from the Logger or Parser class, internally handling raw and decoded data differently.

> Note: This object does not currently support threadding or background operation, so if you wish to emulate and log data from the same device, the objects must exist in separate files ran separately. In a terminal environment you can do this by splitting your terminal, logging in remotely and running a second script there, or just by calling them as parallel processes.

Finally when running instantiating the canSim object, you can pass `loop=True` as an argument if you wish for the object to loop over the provided data indefinitely, otherwise, the process will end after reaching the end of the provided data.

```python
import AcisCanTools as ACT

sim = ACT.sensorSim("logs/field_test.csv", interface="can0", dataFormat="parsed")
try:
    sim.run()
except KeyboardInterrupt:
    print("\n")
    sim.bus.shutdown()
    print("Replay stopped by user.")
```

### Visualizing Logs

Version 0.1.1 introduces the **CanVis** class (pronounced canvis, I know, I'm very clever) that allows for visualization of Parser logs via Matplotlib. While the functionality is currently limited, more will be added in the future.

#### plot_log

This method provides a decently customizable way to visualize an entire log produced by the Parser class. In the future, functionality will be added to select specific chunks of time, as well as support for un-parsed logs from the Logger class.

The function requires a path to a log file and plots NOx, O2, and Other information on three separate plots. Individual sources can be selected, and they can be plotted together or separately as seen below
<div style="display: flex; justify-content: space-evenly; align-items: center; gap: 20px;">
  <img src="assets/notAsOne.png" alt="Separated form" width="300"/>
  <img src="assets/asOne.png" alt="Merged form" width="300"/>
</div>

---

## Example Workflow

### Live NO<sub>x</sub> and O<sub>2</sub> Monitor

```python
import AcisCanTools as ACT
from AcisCanTools import utils as u

log = ACT.Logger(mode="stream", interface=u.get_can_interface())

while True:
    try:
        packet = log.read(timeout=1)
        if packet is not None:
            data = packet.data
            arbitration_id = packet.arbitration_id
            src = u.extract_arbitration_field(arbitration_id, 'src')
            pgn = u.extract_arbitration_field(arbitration_id, 'pgn')
            nox = u.extract_data_field(data, 'nox', convert_raw=False)
            o2 = u.extract_data_field(data, 'o2', convert_raw=False)
            if src != 0:  # Src filtering is unreliable and PGN should be used instead but it's simpler for this isolated test case
                print(f"SRC: {src}")
                print(f"PGN: {pgn}")
                print(f"NOx: {nox:.2f}PPM")
                print(f"02: {o2:.2f}%")
                print("")
        else:
            print("No packet received within timeout period.")
    except KeyboardInterrupt:
        print("\nExiting monitor.")
        log.bus.shutdown()
        break
    except Exception as e:
        print(f"An error occurred: {e}")
        log.bus.shutdown()
        break

```

---
