import re
import subprocess
import can
import csv
import json
import time
from datetime import datetime
from warnings import warn
import os
import pandas as pd
import matplotlib.pyplot as plt


class Logger:
    """
    A class to log CAN messages from a network specified interface using the socketcan bustype.\n
    This class supports both raw data logging and acting as a datastream object to be passes into other methods

    Attributes:
        interface (str): The CAN interface to log from (default: 'can0').
        mode (str): The logging mode, either 'stream' or 'logging' (default: 'stream').
        kwargs (dict): Additional keyword arguments, related for logging mode, more in constructor docstring.
        beginLogging(): Start or resume logging.
        pauseLogging(): Pause logging.
        read(): Read a CAN message from the bus, only available in 'stream' mode.
    """

    def __init__(self, interface='can0', mode='logging', loopback=False, **kwargs):
        """
        Initializes the logger class with the specified interface and mode.\n
        Keyword Args: \n
            \toutput_type (str): The type of output, either 'csv' or 'json' (default: 'csv'). \n
            \toutput_location (str): The relative location to save the output file (default: current dir).\n
            \toutput_name (str): The name of the output file (default: can_log_{timestamp}).
        """
        acceptable_stream_aliases = [
            'stream', 'datastream', 'streaming', 's', 'strm', 'streem', 'strema', 'strem',
            'data-stream', 'data_stream', 'data strm', 'data', 'live', 'livestream', 'live-stream',
            'realtime', 'real-time', 'on-the-fly', 'onfly', 'on_the_fly', 'on the fly',
            'stremaing', 'streming', 'stremm', 'stremming', 'streeming', 'stremaing',
            'strema', 'strea', 'strem', 'stremm', 'streming', 'stremaing',
            'stram', 'strem', 'stremm', 'streming', 'stremaing',
            'sream', 'sreaming', 'sreamm', 'sreamming',
        ]
        acceptable_logged_aliases = [
            'logged', 'log', 'logging', 'l', 'loged', 'loggin', 'logg', 'loggng',
            'logfile', 'log-file', 'log_file', 'log file', 'save', 'saved', 'record', 'recorded',
            'rec', 'recrod', 'recroded', 'recoding', 'recod', 'recodring',
            'archived', 'archive', 'archiv', 'archiving', 'archve', 'archveing',
            'persist', 'persistent', 'persisted', 'persisting',
            'file', 'tofile', 'to_file', 'to-file', 'to file',
            'looged', 'looging', 'loog', 'loogin', 'looged',
        ]
        accepable_kwargs = [kw for kw in [
            'output_type',
            'output_location',
            'output_name',
            # Only exists in inherited Parser class
            'reduced_output' if type(self) is Parser else None,
            # Only exists in inherited Parser class
            'parse_type' if type(self) is Parser else None
        ] if kw is not None]  # Filter out None values that aruse when not class is not inherited

        # Parameters
        self.loopback = loopback
        self.active = False
        # Collect arguments
        self.interface = interface
        self.output_type = kwargs.get('output_type', 'csv')
        self.output_name = kwargs.get(
            'output_name', f"can_log_{datetime.now().strftime('%Y%m%d-%H%M%S')}")
        self.output_location = kwargs.get('output_location', os.getcwd())
        # Mode normalization and validation
        if mode in acceptable_stream_aliases:
            self.mode = 'stream'
        elif mode in acceptable_logged_aliases:
            self.mode = 'logged'
        else:
            raise ValueError(
                f"Mode '{mode}' is not recognized. Use either 'stream' or 'logged'.")

        # Validate arguments
        for keyword in kwargs:
            if keyword not in accepable_kwargs:
                warn(
                    f"Invalid keyword argument: {keyword}, ignoring. \nAcceptable arguments are: {', '.join(accepable_kwargs)}", UserWarning)

        if self.mode == 'stream':
            # Inherited method can use kwards in stream mode, do not throw warning
            if (len(kwargs) > 0 and type(self) is Logger):
                warn(
                    "Provided keyword arguments will be ignored in stream mode", UserWarning)
        if self.mode == 'logged':
            # Warn if the user did not provide these values (i.e., they are set to the default)
            if 'output_type' not in kwargs:
                warn(
                    f"output_type not provided, defaulting to '{self.output_type}'.", UserWarning)
            if 'output_location' not in kwargs:
                warn(
                    f"output_location not provided, defaulting to '{self.output_location}'.", UserWarning)
            if 'output_name' not in kwargs:
                warn(
                    f"output_name not provided, defaulting to '{self.output_name}'.", UserWarning)
            if self.output_type not in ['csv', 'json']:
                raise ValueError("output_type must be either 'csv' or 'json'.")
            if not os.path.exists(self.output_location):
                warn(
                    f"Output location '{self.output_location}' does not exist. Creating it.", UserWarning)
                os.makedirs(self.output_location)

        # Initialize CAN bus
        if self.mode == 'logged':
            self.output_file = os.path.join(
                self.output_location, f"{self.output_name}.{self.output_type}")
        # Init
        self.bus = can.Bus(channel=self.interface, interface='socketcan')

        if self.mode == 'logged':
            if self.output_type == 'csv':
                self._run_csv_logging()
            elif self.output_type == 'json':
                self._run_json_logging()
        elif self.mode == 'stream':
            pass

    def __del__(self):
        """
        Destructor to ensure any open file handles are closed when the object is deleted.
        """
        self._close()
        self.bus.shutdown()
        print("CAN monitor sucessfully closed and resources cleaned up.")

    def beginLogging(self):
        """
        Start or resume logging. If already active, does nothing.
        """
        if self.mode != 'logged':
            warn("beginLogging() can only be called in 'logged' mode.", UserWarning)
            return
        if self.active:
            warn("Logging is already active.", UserWarning)
            return
        self.active = True
        if self.mode == 'logged':
            if self.output_type == 'csv':
                if not hasattr(self, '_csvfile'):
                    self._csvfile = open(
                        self.output_file, mode='a', newline='')
                    self._csvwriter = csv.writer(self._csvfile)
                    if self._csvfile.tell() == 0:
                        self._csvwriter.writerow(
                            ['No.', 'Time', 'Snd/Rc', 'Dest', 'Src', 'Priority', 'PGN', 'Data'])
                self._run_csv_logging()
            elif self.output_type == 'json':
                if not hasattr(self, '_jsonfile'):
                    self._jsonfile = open(self.output_file, mode='a+')
                    self._jsonfile.seek(0, os.SEEK_END)
                    if self._jsonfile.tell() == 0:
                        self._jsonfile.write('[')
                    else:
                        self._jsonfile.seek(self._jsonfile.tell() - 1)
                        self._jsonfile.truncate()
                        self._jsonfile.write(',')
                self._run_json_logging()

    def pauseLogging(self):
        """
        Pause logging. Logging can be resumed later by calling begin().
        """
        if self.mode != 'logged':
            warn("pauseLogging() can only be called in 'logged' mode.", UserWarning)
            return
        if not self.active:
            warn("Logging is already paused.", UserWarning)
            return
        self.active = False

    def _run_csv_logging(self):
        msg_count = 0
        start_time = None
        try:
            while self.active:
                msg = self.bus.recv(timeout=1)
                if msg:
                    if start_time is None:
                        start_time = msg.timestamp
                    msg_count += 1
                    if self.loopback and msg_count % 2 == 0:
                        pass
                    else:
                        rel_time = msg.timestamp - start_time
                        snd_rc = 'Receive'
                        if msg.is_extended_id:
                            priority, pgn, src, dest = self._parse_j1939_id(
                                msg.arbitration_id)
                        else:
                            priority = pgn = src = dest = ''
                        self._csvwriter.writerow([
                            (msg_count if not self.loopback else int((msg_count+1)/2)),
                            f"{rel_time:.3f}",
                            snd_rc,
                            dest,
                            src,
                            priority,
                            pgn,
                            msg.data.hex(' ').upper()
                        ])
        except KeyboardInterrupt:
            print("Logging stopped by user.")

    def _run_json_logging(self):
        msg_count = 0
        start_time = None
        try:
            first = True
            while self.active:
                msg = self.bus.recv(timeout=1)
                if msg:
                    if start_time is None:
                        start_time = msg.timestamp
                    msg_count += 1
                    if self.loopback and msg_count % 2 == 0:
                        pass
                    else:
                        rel_time = msg.timestamp - start_time
                        snd_rc = 'Receive'
                        if msg.is_extended_id:
                            priority, pgn, src, dest = self._parse_j1939_id(
                                msg.arbitration_id)
                        else:
                            priority = pgn = src = dest = ''
                        entry = json.dumps({
                            'No.': (msg_count if not self.loopback else int((msg_count+1)/2)),
                            'Time': f"{rel_time:.3f}",
                            'Snd/Rc': snd_rc,
                            'Dest': dest,
                            'Src': src,
                            'Priority': priority,
                            'PGN': pgn,
                            'Data': msg.data.hex(' ').upper()
                        })
                        if not first:
                            self._jsonfile.write(',\n')
                        self._jsonfile.write(entry)
                        self._jsonfile.flush()
                        first = False
        except KeyboardInterrupt:
            print("Logging stopped by user.")

    def _close(self):
        """
        Close any open file handles. Should be called when done logging.
        """
        if hasattr(self, '_csvfile'):
            self._csvfile.close()
            del self._csvfile
            del self._csvwriter
        if hasattr(self, '_jsonfile'):
            self._jsonfile.write(']')
            self._jsonfile.close()
            del self._jsonfile

    def read(self, timeout=1):
        """
        Read a CAN message from the bus. This is a wrapper for self.bus.recv().
        Args:
            timeout (float): Time in seconds to wait for a message. Default is 1 second.
        Returns:
            can.Message or None: The received CAN message, or None if timeout occurs.
        """
        if self.mode != 'stream':
            warn("read() can only be called in 'stream' mode.", UserWarning)
            return None
        return self.bus.recv(timeout=timeout)

    def _parse_j1939_id(self, arbitration_id):
        """
        Parse a 29-bit J1939 CAN identifier into its component fields.

        The J1939 protocol encodes several fields into a single 29-bit CAN identifier. To extract these fields,
        we use bitwise operations to shift to the start point then use a bitwise AND operation to mask the relevant bits.

        - Priority (3 bits): Bits 26-28.
        - PGN (Parameter Group Number, 18 bits): Bits 8-25.
        - Source Address (8 bits): Bits 0-7.
        - PDU Format (8 bits): Bits 16-23.
        - Destination Address (8 bits): For PDU1 format (PDU Format < 240), bits 8-15 are the destination address (shift right by 8, mask with 0xFF). For PDU2 format (PDU Format >= 240), destination is broadcast (255).

        Args:
            arbitration_id (int): The 29-bit CAN identifier.
        Returns:
            tuple: (priority, pgn, src, dest)
        """
        priority = (arbitration_id >>
                    26) & 0x7  # Extract bits 26-28 for priority
        pgn = (arbitration_id >> 8) & 0x3FFFF    # Extract bits 8-25 for PGN
        src = arbitration_id & 0xFF              # Extract bits 0-7 for source address
        # Extract bits 16-23 for PDU format
        pdu_format = (arbitration_id >> 16) & 0xFF
        if pdu_format < 240:
            # Extract bits 8-15 for destination address
            dest = (arbitration_id >> 8) & 0xFF
        else:
            dest = 255  # Broadcast or not applicable
        return priority, pgn, src, dest


class Parser(Logger):
    """
    A class inherited by the logger class specifically for use when the data section itself must be interpreted.\n
    This class is separate from the logger as while the loggers arbitration_id parsing is specific to the J1939 protocol, the data parsing is not and varies from device to device.\n
    While the logger class automatically parses the arbitration_id, which is a standardized format for all J1939 devices, the data parsing is specific to the device and must be implemented in a subclass of this class.\n
    While this could be implemented in the logger class, it is better to keep create an inherited method for which specific devices can be implemented more specifically.\n

    Attributes:
        interface (str): The CAN interface to log from (default: 'can0').
        mode (str): The logging mode, either 'stream' or 'logging' (default: 'stream').
        kwargs (dict): Additional keyword arguments, related for logging mode, more in constructor docstring.
        beginLogging(): Start or resume logging.
        pauseLogging(): Pause logging.
        read(): Read a CAN message from the bus, only available in 'stream' mode.
        change_data_source(): Currently not implemented, will change the data source to a different device type.\n
    """

    def __init__(self, interface='can0', mode='logging', loopback=False, **kwargs):
        """
        Initializes the logger class with the specified interface and mode.\n
        Keyword Args: \n
            \toutput_type (str): The type of output, either 'csv' or 'json' (default: 'csv'). \n
            \toutput_location (str): The relative location to save the output file (default: current dir).\n
            \toutput_name (str): The name of the output file (default: can_log_{timestamp}).\n
            \treduced_output (bool): If True, automatically drops any arbitration info from all output forms, only giving parsed data (default: False).\n
            \tparse_type (str): The specific device output to be parsed, currently only supports Contenential Smart NOx Sensor, 'smart_nox' (default: 'smart_nox').\n
            \tloopback (bool): Set to true to prevent packets from being logged twice when your interface is operating in loopback mode (this is a cool way of saying the logger ignores every other packet)
        """
        # Parameters
        self.parse_type = kwargs.get('parse_type', 'smart_nox')
        self.reduced_output = kwargs.get('reduced_output', False)
        # Will be set to the specific device type after it is setup, e.g., 'smart_nox'
        self.configured_for = []
        super().__init__(interface=interface, mode=mode, loopback=loopback, **kwargs)

        acceptable_parse_aliases = [  # Currently only supports this one
            'smart_nox'
        ]

        # Validate arguments
        if self.parse_type not in acceptable_parse_aliases:
            raise ValueError(
                f"parse_type '{self.parse_type}' is not recognized. Use one of: {', '.join(acceptable_parse_aliases)}.")

        if "parse_type" not in kwargs:
            warn(
                f"parse_type not provided, defaulting to '{self.parse_type}'.", UserWarning)

        if type(self.reduced_output) is not bool:
            raise TypeError("reduced_output must be a boolean value.")

    def configure_smart_nox_output(self, nox_raw=True, o2_raw=True, status=True, heater=True, error_nox=True, error_o2=True, internal=False):
        """
        Configure the output for the Smart NOx Sensor data.
        If you wish to exclude any data from the output, set the corresponding parameter to False.\n
        When ran with no arguments all data will be included in the output and only fields you wish to exclude need to be passed

        Args:
            nox_raw (bool): If True, include NOx data in output.
            o2_raw (bool): If True, include O2 data in output.
            status (bool): If True, include status byte in output.
            heater (bool): If True, include heater byte in output.
            error_nox (bool): If True, include NOx error byte in output.
            error_o2 (bool): If True, include O2 error byte in output.
            internal (bool): internal boolean used to indicate the nature of the call, do not pass this argument
        """
        if 'smart_nox' not in self.configured_for and not internal:
            self.configured_for.append('smart_nox')
        self.nox_raw = nox_raw
        self.o2_raw = o2_raw
        self.status = status
        self.heater = heater
        self.error_nox = error_nox
        self.error_o2 = error_o2

    def _smart_nox_decode(self, data):
        """
        Decode the 8-byte payload from the sensor according to Table 4.1.1 of the datasheet.

        Args:
            data (bytes): 8-byte CAN data payload.
        Returns:
            tuple: (nox_raw, o2_raw, status, heater, error_nox, error_o2)
                - nox_raw: Unsigned 16-bit integer, bytes 0-1, little-endian
                - o2_raw: Unsigned 16-bit integer, bytes 2-3, little-endian
                - status: Unsigned 8-bit integer, byte 4
                - heater: Unsigned 8-bit integer, byte 5
                - error_nox: Unsigned 8-bit integer, byte 6
                - error_o2: Unsigned 8-bit integer, byte 7
        """
        if 'smart_nox' not in self.configured_for:
            warn("Parser is not explicitly configured for Smart NOx Sensor output. Please call configure_smart_nox_output() first, using default configuration", UserWarning)
            self.configure_smart_nox_output(internal=True)
        nox_raw = int.from_bytes(
            data[0:2], 'little', signed=False) if self.nox_raw else 0
        o2_raw = int.from_bytes(
            data[2:4], 'little', signed=False) if self.o2_raw else 0
        status = data[4] if self.status else 0
        heater = data[5] if self.heater else 0
        error_nox = data[6] if self.error_nox else 0
        error_o2 = data[7] if self.error_o2 else 0

        # When excluding data, we simply set the value to 0 instead of none to prevent issues with CSV and JSON output/formatting
        return nox_raw, o2_raw, status, heater, error_nox, error_o2

    def _run_csv_logging(self):
        collectPacket = True
        msg_count = 0
        start_time = None
        try:
            # Prepare CSV file if not already open
            if not hasattr(self, '_csvfile'):
                self._csvfile = open(self.output_file, mode='a', newline='')
                self._csvwriter = csv.writer(self._csvfile)
                if self._csvfile.tell() == 0:
                    if self.reduced_output:
                        self._csvwriter.writerow(
                            ['No.', 'Time', 'NOx Raw', 'O2 Raw', 'Status', 'Heater', 'Error NOx', 'Error O2'])
                    else:
                        self._csvwriter.writerow(['No.', 'Time', 'Snd/Rc', 'Dest', 'Src', 'Priority',
                                                 'PGN', 'NOx Raw', 'O2 Raw', 'Status', 'Heater', 'Error NOx', 'Error O2'])
            while self.active:
                msg = self.bus.recv(timeout=1)
                if msg:
                    if start_time is None:
                        start_time = msg.timestamp
                    msg_count += 1
                    if self.loopback and msg_count % 2 == 0:
                        pass  # Skip every other message if loopback is enabled
                    else:
                        rel_time = msg.timestamp - start_time
                        snd_rc = 'Receive'
                        if msg.is_extended_id:
                            priority, pgn, src, dest = self._parse_j1939_id(
                                msg.arbitration_id)
                        else:
                            priority = pgn = src = dest = ''
                        nox_raw, o2_raw, status, heater, error_nox, error_o2 = self._smart_nox_decode(
                            msg.data)
                        if self.reduced_output:
                            self._csvwriter.writerow([
                                (msg_count if not self.loopback else int(
                                    (msg_count+1)/2)),
                                f"{rel_time:.3f}",
                                nox_raw, o2_raw, status, heater, error_nox, error_o2
                            ])
                        else:
                            self._csvwriter.writerow([
                                (msg_count if not self.loopback else int(
                                    (msg_count+1)/2)),
                                f"{rel_time:.3f}",
                                snd_rc,
                                dest,
                                src,
                                priority,
                                pgn,
                                nox_raw, o2_raw, status, heater, error_nox, error_o2
                            ])
        except KeyboardInterrupt:
            print("Logging stopped by user.")

    def _run_json_logging(self):
        msg_count = 0
        start_time = None
        try:
            if not hasattr(self, '_jsonfile'):
                self._jsonfile = open(self.output_file, mode='a+')
                self._jsonfile.seek(0, os.SEEK_END)
                if self._jsonfile.tell() == 0:
                    self._jsonfile.write('[')
                else:
                    self._jsonfile.seek(self._jsonfile.tell() - 1)
                    self._jsonfile.truncate()
                    self._jsonfile.write(',')
            first = True
            while self.active:
                msg = self.bus.recv(timeout=1)
                if msg:
                    if start_time is None:
                        start_time = msg.timestamp
                    msg_count += 1
                    if self.loopback and msg_count % 2 == 0:
                        pass  # Skip every other message if loopback is enabled
                    else:
                        rel_time = msg.timestamp - start_time
                        snd_rc = 'Receive'
                        if msg.is_extended_id:
                            priority, pgn, src, dest = self._parse_j1939_id(
                                msg.arbitration_id)
                        else:
                            priority = pgn = src = dest = ''
                        nox_raw, o2_raw, status, heater, error_nox, error_o2 = self._smart_nox_decode(
                            msg.data)
                        if self.reduced_output:
                            entry = json.dumps({
                                'No.': (msg_count if not self.loopback else int((msg_count+1)/2)),
                                'Time': f"{rel_time:.3f}",
                                'NOx Raw': nox_raw,
                                'O2 Raw': o2_raw,
                                'Status': status,
                                'Heater': heater,
                                'Error NOx': error_nox,
                                'Error O2': error_o2
                            })
                        else:
                            entry = json.dumps({
                                'No.': (msg_count if not self.loopback else int((msg_count+1)/2)),
                                'Time': f"{rel_time:.3f}",
                                'Snd/Rc': snd_rc,
                                'Dest': dest,
                                'Src': src,
                                'Priority': priority,
                                'PGN': pgn,
                                'NOx Raw': nox_raw,
                                'O2 Raw': o2_raw,
                                'Status': status,
                                'Heater': heater,
                                'Error NOx': error_nox,
                                'Error O2': error_o2
                            })
                        if not first:
                            self._jsonfile.write(',\n')
                        self._jsonfile.write(entry)
                        self._jsonfile.flush()
                        first = False
        except KeyboardInterrupt:
            print("Logging stopped by user.")

    def change_data_source(self, mode):
        """
        Change the mode of the logger to either 'stream' or 'logged'.
        This will reinitialize the logger with the new mode.

        Args:
            mode (str): The new mode, either 'stream' or 'logged'.
        """
        warn("this method is not yet implemented as there is currently only one data source supported", UserWarning)
        pass


class utils:
    """
    A static class containing various helpful methods for working with the AcisCanTools codebase.\n
    """

    def __init__(self):
        """
        Just don't...
        """
        print("[AcisCanTools] I'm not gonna throw an error like some kind of dictator but for future refrence, the utils class is entirely static so there was not much point in creating an instance of it")
        print("[AcisCanTools] By all means though, have fun with your new utils object, I'm not here to judge")

    @staticmethod
    def static_decode(data, device="smart_nox"):
        """
        Similar to the private methods used within the Logger classes, however this one is designed to be called statically,
        passing a single data packet as a utility

        Args:
            data (bytes): The 8-byte CAN data payload to decode.
            device (str): The type of device to decode, currently only supports 'smart_nox'.
        Returns:
            tuple: (nox_raw, o2_raw, status, heater, error_nox, error_o2) if device is 'smart_nox'.
        Raises:
            ValueError: If the device type is not supported or invalid data is provided.

        """
        if data is not None:
            if device == "smart_nox":
                nox_raw = int.from_bytes(data[0:2], 'little', signed=False)
                o2_raw = int.from_bytes(data[2:4], 'little', signed=False)
                status = data[4]
                heater = data[5]
                error_nox = data[6]
                error_o2 = data[7]
                return nox_raw, o2_raw, status, heater, error_nox, error_o2
            else:
                raise ValueError(
                    f"Device '{device}' is not supported for static decoding.")
        else:
            raise ValueError("Data must be provided for static decoding.")

    @staticmethod
    def get_can_interface(verbose=False):
        """
        Static method to get the first available CAN interface on the system.\n
        This method uses the 'ip link show type can' command to list CAN interfaces and returns the first one found.\n
        Args:
            verbose (bool): If True, returns the full output of the command as a string. If False, returns only the first interface name found.
        Returns:
            str: The name of the first CAN interface found, or None if no interfaces are found.\n
            If verbose is True, returns the full output of the command as a string.
        """
        try:
            output = subprocess.check_output(
                "ip link show type can", shell=True, text=True)
            if verbose:
                return output  # Return the full output as a string
            # Not verbose: extract the first interface name
            for line in output.splitlines():
                match = re.match(r"\d+:\s*([^\s:]+):", line)
                if match:
                    # Return the interface name as a string
                    return match.group(1)
            print("No CAN interfaces found, but no errors were thrown.")
            return ""  # No interface found
        except Exception as e:
            if verbose:
                print(f"Error fetching CAN interfaces: {e}")
            return ""

    @staticmethod
    def check_can_status():
        """
        Returns the first CAN interface name and its status (e.g., 'UP') found on the system.
        Returns:
            string: status or None if not found.
        """
        try:
            output = subprocess.check_output(
                "ip link show type can", shell=True, text=True)
            for line in output.splitlines():
                # Match lines like: '3: can0: <NOARP,UP,LOWER_UP,ECHO> mtu ...'
                match = re.match(r"\d+:\s*([^\s:]+):\s*<([^>]*)>", line)
                if match:
                    iface = match.group(1)
                    flags = match.group(2)
                    # Status is 'UP' if present in flags
                    status = 'UP' if 'UP' in flags.split(',') else 'DOWN'
                    return status
            return None
        except Exception as e:
            print(f"Error fetching CAN interfaces: {e}")
            return None

    @staticmethod
    def convert_NOx(rawVal):
        """
        Converts a list of raw NOx values to a list of NOx concentrations in ppm.
        The conversion is based on the formula: NOx (ppm) = (raw value * .05) - 200

        Args:
            rawVal (int): A single raw NOx value to convert to PPM.

        Returns:
            float: A converted NOx concentration in ppm.
        """
        return ((rawVal * .05) - 200)

    @staticmethod
    def convert_O2(rawVal):
        """
        Converts a list of raw O2 values to a list of O2 concentrations in ppm.
        The conversion is based on the formula: O2 (ppm) = (raw value * .000514) - 12

        Args:
            rawVal (int): A single raw O2 value to be converted to percentage.

        Returns:
            float: A converted O2 concentration in percentage.
        """
        return ((rawVal * .000514)-12)

    @staticmethod
    def extract_arbitration_field(arbitration_id, field):
        """
        Extracts the arbitration field from a given field name.
        This is useful for parsing J1939 arbitration IDs.

        Args:
            arbitration_id (int): The arbitration ID to extract the field from.
            field (str): The field name to extract the arbitration value from.

        Returns:
            int: The extracted arbitration value.
        """
        destAliases = ["dest", "destination", "d"]
        srcAliases = ["src", "source", "s"]
        priorityAliases = ["priority", "p", "prio"]
        pgnAliases = ["pgn", "p", "param_group_number",
                      "param_group_num", "param_group"]

        # Extract bits 26-28 for priority
        priority = (arbitration_id >> 26) & 0x7
        pgn = (arbitration_id >> 8) & 0x3FFFF    # Extract bits 8-25 for PGN
        src = arbitration_id & 0xFF              # Extract bits 0-7 for source address
        # Extract bits 16-23 for PDU format
        pdu_format = (arbitration_id >> 16) & 0xFF
        if pdu_format < 240:
            # Extract bits 8-15 for destination address
            dest = (arbitration_id >> 8) & 0xFF
        else:
            dest = 255  # Broadcast or not applicable

        if field.lower() in destAliases:
            return dest
        elif field.lower() in srcAliases:
            return src
        elif field.lower() in priorityAliases:
            return priority
        elif field.lower() in pgnAliases:
            return pgn
        else:
            raise ValueError(
                f"Field '{field}' is not recognized. Use one of: {', '.join(destAliases + srcAliases + priorityAliases + pgnAliases)}.")

    @staticmethod
    def extract_data_field(data, field, convert_raw=False):
        """
        Extracts the data field from a given field name.

        Args:
            data (int list): The data packet to extract the field from.
            field (str): The field name to extract the data field from.
            convert_raw (bool): If True, applies conversion factors to the raw O2 or NOx value.

        Returns:
            int: The extracted data value.
        """
        NOxAliases = ["nox", "nox_raw", "nox_raw_value", "nox_raw_data"]
        O2Aliases = ["o2", "o2_raw", "o2_raw_value", "o2_raw_data"]
        statusAliases = ["status", "status_byte", "status_data"]
        heaterAliases = ["heater", "heater_byte", "heater_data"]
        errorNOxAliases = ["error_nox", "error_nox_byte", "error_nox_data"]
        errorO2Aliases = ["error_o2", "error_o2_byte", "error_o2_data"]
        data = utils.static_decode(data)
        if field.lower() in NOxAliases:
            return data[0] if not convert_raw else utils.convert_NOx(data[0])
        elif field.lower() in O2Aliases:
            return data[1] if not convert_raw else utils.convert_O2(data[1])
        elif field.lower() in statusAliases:
            return data[2]
        elif field.lower() in heaterAliases:
            return data[3]
        elif field.lower() in errorNOxAliases:
            return data[4]
        elif field.lower() in errorO2Aliases:
            return data[5]
        else:
            raise ValueError(
                f"Field '{field}' is not recognized. Use one of: {', '.join(NOxAliases + O2Aliases + statusAliases + heaterAliases + errorNOxAliases + errorO2Aliases)}.")

    @staticmethod
    def extract_csv_field(file, field, source, sourceType="src", convert_raw=False):
        """
        Extracts time and field values from a desired field and source from a CSV log

        Args:
            file (str | pd.DataFrame): The path to the CSV file to extract data from or a pandas DataFrame.
            field (str): The field name to extract data from.
            source (int): The source ID to filter the data by.
            sourceType (str): The type of source, either 'src' or 'pgn'. Default is 'src'.
            convert_raw (bool): If True, applies conversion factors to the raw O2 or NOx value.
        Returns:
            tuple: (time, field_value) where both are one-dimensional pandas Series.
        Raises:
            ValueError: If the field or source type is not recognized.
        """

        NOxAliases = ["nox", "nox_raw", "nox_raw_value", "nox_raw_data"]
        O2Aliases = ["o2", "o2_raw", "o2_raw_value", "o2_raw_data"]
        statusAliases = ["status", "status_byte", "status_data"]
        heaterAliases = ["heater", "heater_byte", "heater_data"]
        errorNOxAliases = ["error_nox", "error_nox_byte", "error_nox_data"]
        errorO2Aliases = ["error_o2", "error_o2_byte", "error_o2_data"]

        if isinstance(file, pd.DataFrame):
            data = file
        else:
            data = pd.read_csv(file)

        timeComponent = None
        if (sourceType.lower() == "src"):
            data = data.loc[data.Src == source]
        elif (sourceType.lower() == "pgn"):
            data = data.loc[data.PGN == source]
        else:
            raise ValueError(
                f"Source type '{sourceType}' is not a source, use 'src' or 'pgn'")

        fieldVal = None
        if field.lower() in NOxAliases:
            fieldVal = data["NOx Raw"] if not convert_raw else utils.convert_NOx(
                data["NOx Raw"])
        elif field.lower() in O2Aliases:
            fieldVal = data["O2 Raw"] if not convert_raw else utils.convert_NOx(
                data["O2 Raw"])
        elif field.lower() in statusAliases:
            fieldVal = data.Status
        elif field.lower() in heaterAliases:
            fieldVal = data.Heater
        elif field.lower() in errorNOxAliases:
            fieldVal = data["Error NOx"]
        elif field.lower() in errorO2Aliases:
            fieldVal = data["Error O2"]
        else:
            raise ValueError(
                f"Field '{field}' is not recognized. Use one of: {', '.join(NOxAliases + O2Aliases + statusAliases + heaterAliases + errorNOxAliases + errorO2Aliases)}.")

        return (data.Time, fieldVal)

    @staticmethod
    def isolate_source(file, source, sourceType="src"):
        """
        Isolates a source from a CSV log file based on the source type and returns a dataframe for that source.
        Args:
            file (str | pd.DataFrame): The path to the CSV file to extract data from or a pandas DataFrame.
            source (int): The source ID to filter the data by.
            sourceType (str): The type of source, either 'src' or 'pgn'. Default is 'src'.
        """

        if isinstance(file, pd.DataFrame):
            data = file
        else:
            data = pd.read_csv(file)

        if (sourceType.lower() == "src"):
            data = data.loc[data.Src == source]
        elif (sourceType.lower() == "pgn"):
            data = data.loc[data.PGN == source]
        else:
            raise ValueError(
                f"Source type '{sourceType}' is not a source, use 'src' or 'pgn'")

        return data


class sensorSim:
    """
    Simulates a CAN sensor by replaying messages from a CSV log (Logger or Parser format) onto a CAN interface.
    Messages are reconstructed as python-can Message objects and sent to the specified interface, matching original timing.
    The class can be used as a drop-in replacement for a real CAN bus for testing/logging.
    """

    def __init__(self, inputFile, interface='can0', dataFormat='parsed'):
        self.interface = interface
        self.dataFormat = dataFormat.lower()
        self.inputFile = inputFile
        self.messages = []  # List of (timestamp, can.Message)
        self._load_csv()
        self.bus = can.Bus(channel=self.interface, interface='socketcan')
        self._replay_thread = None
        self._stop_replay = False

    def _load_csv(self):
        self.messages = []
        with open(self.inputFile, 'r') as f:
            reader = csv.reader(f)
            header = next(reader)
            if self.dataFormat == 'parsed':
                time_idx = header.index('Time')
                src_idx = header.index('Src')
                dest_idx = header.index('Dest')
                prio_idx = header.index('Priority')
                pgn_idx = header.index('PGN')
                # Indices for parsed fields
                nox_idx = header.index('NOx Raw')
                o2_idx = header.index('O2 Raw')
                status_idx = header.index('Status')
                heater_idx = header.index('Heater')
                error_nox_idx = header.index('Error NOx')
                error_o2_idx = header.index('Error O2')
            elif self.dataFormat == 'raw':
                time_idx = header.index('Time')
                src_idx = header.index('Src')
                dest_idx = header.index('Dest')
                prio_idx = header.index('Priority')
                pgn_idx = header.index('PGN')
                data_idx = header.index('Data')
            else:
                raise ValueError("dataFormat must be 'parsed' or 'raw'")
            for row in reader:
                try:
                    timestamp = float(row[time_idx])
                    src = int(row[src_idx]) if row[src_idx] else 0
                    dest = int(row[dest_idx]) if row[dest_idx] else 0
                    prio = int(row[prio_idx]) if row[prio_idx] else 0
                    pgn = int(row[pgn_idx]) if row[pgn_idx] else 0
                    arbitration_id = (prio << 26) | (pgn << 8) | src
                    if self.dataFormat == 'parsed':
                        # Build 8-byte payload from parsed columns
                        nox = int(row[nox_idx]) if row[nox_idx] else 0
                        o2 = int(row[o2_idx]) if row[o2_idx] else 0
                        status = int(row[status_idx]) if row[status_idx] else 0
                        heater = int(row[heater_idx]) if row[heater_idx] else 0
                        error_nox = int(row[error_nox_idx]
                                        ) if row[error_nox_idx] else 0
                        error_o2 = int(row[error_o2_idx]
                                       ) if row[error_o2_idx] else 0
                        # NOx and O2 are 2 bytes each, little-endian
                        data_bytes = (
                            nox.to_bytes(2, 'little', signed=False) +
                            o2.to_bytes(2, 'little', signed=False) +
                            bytes([status, heater, error_nox, error_o2])
                        )
                    else:
                        # Raw: use Data column, pad to 8 bytes
                        data_bytes = bytes.fromhex(row[data_idx].replace(
                            ' ', '')) if row[data_idx] else b''
                        if len(data_bytes) < 8:
                            data_bytes = data_bytes + \
                                bytes(8 - len(data_bytes))
                    msg = can.Message(
                        arbitration_id=arbitration_id,
                        data=data_bytes,
                        is_extended_id=True
                    )
                    self.messages.append((timestamp, msg))
                except Exception as e:
                    continue  # Skip malformed rows

    def run(self, loop=False):
        """
        Replay the loaded messages onto the CAN interface, matching original timing.
        If loop=True, repeats indefinitely.
        """
        self._stop_replay = False
        while not self._stop_replay:
            if not self.messages:
                break
            start_time = time.time()
            first_ts = self.messages[0][0]
            for i, (ts, msg) in enumerate(self.messages):
                if self._stop_replay:
                    break
                now = time.time()
                # Wait for the correct relative time
                rel_time = ts - first_ts
                sleep_time = start_time + rel_time - now
                if sleep_time > 0:
                    time.sleep(sleep_time)
                try:
                    self.bus.send(msg)
                except Exception:
                    pass
            if not loop:
                break

    def stop(self):
        """Stop replaying messages."""
        self._stop_replay = True

    def __del__(self):
        self.stop()
        if hasattr(self, 'bus'):
            self.bus.shutdown()


class canVis:
    """
    canVis (pronounced "canvis") is a class containing various methods and tools for CAN-visualization.
    This class is not fully implemented yet, but will be used to visualize CAN data in a more user-friendly way.
    """

    @staticmethod
    def plot_field(file, field, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), minTime=None, maxTime=None):
        """
        Plots a single specified time-dependent field from a provided CSV file generated from this package

        Args:
            file (str): Path to the CSV file containing data.
            raw (bool): If True, plots raw NOx/O2 values. If False, plots converted values.
            srcList (list): List of source addresses to collect data from, plots all if not provided.
            excludeSrc (list): List of sources/addresses to ignore, ignored if srcList is not None
            sourceType (str): The type of source to filter by, either 'src' or 'PGN', src by default.
            save (bool): Determines wether or not to save the plot(s)
            show(bool): Determines wether or not to display the plot(s) (forced to true if save is false)
            outputName (string): Desired path and name for saved figures(defaults to current date and time)
            minTime (int): The minimum timestamp to be plotted (default: lowest value)
            maxTime (int): The maximum timestamp to be plotted (defult: largest value)


        Raises:
            ValueError: Can rise for many reasons, all likely due to improperly formatted CSV files and/or incorrect parameters.
            FileNotFoundError: If the specified file does not exist.
        """

        nox_aliases = ["nox", "nox raw", "nox_raw",
                       "raw nox", "noxraw", "rawnox"]
        o2_aliases = ["o2", "o2 raw", "o2_raw", "raw o2", "o2Raw", "rawo2"]

        if field.lower() in nox_aliases:
            field = "NOx Raw"
        if field.lower() in o2_aliases:
            field = "O2 Raw"
        if field.lower() == "heater":
            field = "Heater"
        if field.lower() == "status":
            field = "Status"
        if "nox" in field.lower() and field.lower() not in nox_aliases:
            field = "Error NOx"
        if "o2" in field.lower() and field.lower() not in o2_aliases:
            field = "Error O2"

        if not save:
            show = True
        # Setup
        data = pd.read_csv(file)

        if (minTime is None):
            minTime = data.Time.min()
        if (maxTime is None):
            maxTime = data.Time.max()

        if sourceType.lower() not in ['src', 'pgn']:
            raise ValueError("sourceType must be either 'src' or 'PGN'.")
        elif sourceType.lower() == 'src' and "Src" not in data.columns:
            raise ValueError(
                "CSV file must contain 'Src' column when sourceType is 'src'.")
        elif sourceType.lower() == 'pgn' and "PGN" not in data.columns:
            raise ValueError(
                "CSV file must contain 'PGN' column when sourceType is 'PGN'.")

        for col in [field, 'Time']:
            if col not in data.columns:
                raise ValueError(
                    f"CSV file must contain '{col}' column if you wish to plot it.")

        if srcList is None:
            if sourceType.lower() == 'src':
                srcList = data.Src.unique()
            else:
                srcList = data.PGN.unique()

        srcList = [
            src for src in srcList if src not in excludeSrc] if excludeSrc is not None else srcList

        for src in srcList:
            current = data.loc[data.Src == src] if sourceType.lower(
            ) == "src" else data.loc[data.PGN == src]

            current = current.loc[current.Time >= minTime]
            current = current.loc[current.Time <= maxTime]
            if (field == "NOx Raw"):
                plt.plot(current.Time,
                         (current["NOx Raw"] if raw else utils.convert_NOx(current["NOx Raw"])), label=(f"{sourceType}: {src}"))
            elif (field == "O2 Raw"):
                plt.plot(current.Time,
                         (current["O2 Raw"] if raw else utils.convert_NOx(current["O2 Raw"])), label=(f"{sourceType}: {src}"))
            else:
                plt.plot(current.Time, current[field],
                         label=f"{sourceType}: {src}")

        plt.legend()
        if ("Raw" in field and not raw):
            if (field == "NOx Raw"):
                plt.title(f"NOx Values from {file} (PPM)")
            else:
                plt.title(f"O2 Values from {file} (%)")
        else:
            plt.title(f"{field} values from {file}")

        if save:
            plt.savefig(outputName)
        if show:
            plt.show()

    @staticmethod
    def plot_NOx(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), maxTime=None, minTime=None):
        """
        Wrapper for Plot Field automatically specifying NOx\n
        See plot_field() for argument information
        """
        canVis.plot_field(field="NOx", file=file, raw=raw, srcList=srcList, excludeSrc=excludeSrc,
                          sourceType=sourceType, save=save, show=show, outputName=outputName, maxTime=maxTime, minTime=minTime)

    @staticmethod
    def plot_O2(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), maxTime=None, minTime=None):
        """
        Wrapper for Plot Field automatically specifying O2\n
        See plot_field() for argument information
        """
        canVis.plot_field(field="o2", file=file, raw=raw, srcList=srcList, excludeSrc=excludeSrc,
                          sourceType=sourceType, save=save, show=show, outputName=outputName, maxTime=maxTime, minTime=minTime)

    @staticmethod
    def plot_status(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), maxTime=None, minTime=None):
        """
        Wrapper for Plot Field automatically specifying Status\n
        See plot_field() for argument information
        """
        canVis.plot_field(field="Status", file=file, raw=raw, srcList=srcList, excludeSrc=excludeSrc,
                          sourceType=sourceType, save=save, show=show, outputName=outputName, maxTime=maxTime, minTime=minTime)

    @staticmethod
    def plot_heater(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), maxTime=None, minTime=None):
        """
        Wrapper for Plot Field automatically specifying Heater\n
        See plot_field() for argument information
        """
        canVis.plot_field(field="Heater", file=file, raw=raw, srcList=srcList, excludeSrc=excludeSrc,
                          sourceType=sourceType, save=save, show=show, outputName=outputName, maxTime=maxTime, minTime=minTime)

    @staticmethod
    def plot_error_NOx(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), maxTime=None, minTime=None):
        """
        Wrapper for Plot Field automatically specifying Error NOx\n
        See plot_field() for argument information
        """
        canVis.plot_field(field="Error NOx", file=file, raw=raw, srcList=srcList, excludeSrc=excludeSrc,
                          sourceType=sourceType, save=save, show=show, outputName=outputName, maxTime=maxTime, minTime=minTime)

    @staticmethod
    def plot_error_O2(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), maxTime=None, minTime=None):
        """
        Wrapper for Plot Field automatically specifying Error O2\n
        See plot_field() for argument information
        """
        canVis.plot_field(field="Error O2", file=file, raw=raw, srcList=srcList, excludeSrc=excludeSrc,
                          sourceType=sourceType, save=save, show=show, outputName=outputName, maxTime=maxTime, minTime=minTime)

    @staticmethod
    def plot_log(file, raw=True, srcList=None, excludeSrc=None, sourceType="src", asOne=False, save=False, show=True, outputName=datetime.now().strftime('%Y%m%d-%H%M%S'), minTime=None, maxTime=None):
        """
        Plot any specified time-dependent data from a provided AcisCanTools parser file

        - Generates a three plots per source, one for NOx, one for 02, and a third for the status, heater, and error bytes.\n
        - If asOne is true, all selected SRCs will be placed into a single figure, still containing two subplots, if false, a figure will be created for each source
        - Only 4 line styles are possible so asOne will be ignored and all data will be plotted separately if length(srcList) > 4
        Args:
            file (str): Path to the CSV file containing data.
            raw (bool): If True, plots raw NOx/O2 values. If False, plots converted values.
            srcList (list): List of source addresses to collect data from, plots all if not provided.
            excludeSrc (list): List of sources/addresses to ignore, ignored if srcList is not None
            sourceType (str): The type of source to filter by, either 'src' or 'PGN', src by default.
            asOne (bool): If True, plots all data in one figure. If False, creates separate figures for each field.
            save (bool): Determines wether or not to save the plot(s)
            show(bool): Determines wether or not to display the plot(s) (forced to true if save is false)
            outputName (string): Desired path and name for saved figures(defaults to current date and time)
            minTime (int): The minimum timestamp to be plotted (default: lowest value)
            maxTime (int): The maximum timestamp to be plotted (defult: largest value)


        Raises:
            ValueError: Can rise for many reasons, all likely due to improperly formatted CSV files and/or incorrect parameters.
            FileNotFoundError: If the specified file does not exist.
        """

        # Setup
        data = pd.read_csv(file)

        if (minTime is None):
            minTime = data.Time.min()
        if (maxTime is None):
            maxTime = data.Time.max()

        if srcList is not None and len(srcList) > 4:
            asOne = False

        if not save:
            show = True

        lineTypes = ['-', '--', '-.', ':']

        if srcList is None:
            if sourceType.lower() == 'src':
                srcList = data.Src.unique()
            else:
                srcList = data.PGN.unique()

        # Blacklist specified sources
        srcList = [
            src for src in srcList if src not in excludeSrc] if excludeSrc is not None else srcList

        # Handle errors
        if 'Time' not in data.columns:
            raise ValueError("CSV file must contain 'Time' column.")
        if sourceType.lower() not in ['src', 'pgn']:
            raise ValueError("sourceType must be either 'src' or 'PGN'.")
        elif sourceType.lower() == 'src' and "Src" not in data.columns:
            raise ValueError(
                "CSV file must contain 'Src' column when sourceType is 'src'.")
        elif sourceType.lower() == 'pgn' and "PGN" not in data.columns:
            raise ValueError(
                "CSV file must contain 'PGN' column when sourceType is 'PGN'.")

        for col in ['NOx Raw', 'O2 Raw', 'Status', 'Heater', 'Error NOx', 'Error O2']:
            if col not in data.columns:
                raise ValueError(
                    f"CSV file must contain '{col}' column if you wish to plot it.")

        if not asOne:
            fig, axes = plt.subplots(
                # Figsize is done such that the figure scales linearly and 2 sources creates 16x9
                len(srcList), 3, figsize=(16, 4.5*len(srcList)))
            plt.subplots_adjust(hspace=0.5, wspace=0.3)
            for i, src in enumerate(srcList):
                # Create temp dataframe with only desired src
                if (sourceType.lower() == 'src'):
                    current = data.loc[data.Src == src]
                else:
                    current = data.loc[data.PGN == src]

                current = current.loc[current.Time >= minTime]
                current = current.loc[current.Time <= maxTime]

                noxPlot = axes[i][0]
                o2Plot = axes[i][1]
                otherPlot = axes[i][2]

                noxPlot.set_title(
                    f"NOx for {"Src" if sourceType.lower() == "src" else "PGN"}: {src}", pad=20)
                o2Plot.set_title(
                    f"O2 for {"Src" if sourceType.lower() == "src" else "PGN"}: {src}", pad=20)
                otherPlot.set_title(
                    f"Other Data for {"Src" if sourceType.lower() == "src" else "PGN"}: {src}", pad=20)

                nox = current["NOx Raw"] if raw else utils.convert_NOx(
                    current["NOx Raw"])
                o2 = current["O2 Raw"] if raw else utils.convert_O2(
                    current["O2 Raw"])

                noxPlot.plot(current.Time, nox, label=(
                    "Raw NOx" if raw else "NOx")+" (PPM)")
                noxPlot.legend()
                o2Plot.plot(current.Time, o2, label=(
                    "Raw O2" if raw else "O2") + "(%)")
                o2Plot.legend()

                otherPlot.plot(current.Time, current.Status, label="Status")
                otherPlot.plot(current.Time, current.Heater, label="Heater")
                otherPlot.plot(
                    current.Time, current["Error NOx"], label="Error NOx")
                otherPlot.plot(
                    current.Time, current["Error O2"], label="Error O2")
                otherPlot.legend(bbox_to_anchor=(.955, 0.5), loc='center left')
        else:
            fig, axes = plt.subplots(3, 1, figsize=(16, 9))
            plt.subplots_adjust(hspace=0.5, wspace=0.3)
            for i, src in enumerate(srcList):
                if (sourceType.lower() == 'src'):
                    current = data.loc[data.Src == src]
                else:
                    current = data.loc[data.PGN == src]

                current = current.loc[current.Time >= minTime]
                current = current.loc[current.Time <= maxTime]

                noxPlot = axes[0]
                o2Plot = axes[1]
                otherPlot = axes[2]

                noxPlot.set_title("NOx")
                o2Plot.set_title("O2")
                otherPlot.set_title("Other Data")

                nox = current["NOx Raw"] if raw else utils.convert_NOx(
                    current["NOx Raw"])
                o2 = current["O2 Raw"] if raw else utils.convert_O2(
                    current["O2 Raw"])

                noxPlot.plot(current.Time, nox, lineTypes[i], label=(
                    "Raw NOx" if raw else "NOx") + f" (PPM) ({src})")
                noxPlot.legend(bbox_to_anchor=(.955, 0.5), loc='center left')
                o2Plot.plot(current.Time, o2, label=(
                    "Raw O2" if raw else "O2") + f"(%) ({src})")
                o2Plot.legend(bbox_to_anchor=(.955, 0.5), loc='center left')

                otherPlot.plot(
                    current.Time, current.Status, lineTypes[i], label=f"Status ({src})")
                otherPlot.plot(
                    current.Time, current.Heater, lineTypes[i], label=f"Heater ({src})")
                otherPlot.plot(
                    current.Time, current["Error NOx"], lineTypes[i], label=f"Error NOx ({src})")
                otherPlot.plot(
                    current.Time, current["Error O2"], lineTypes[i], label=f"Error O2 ({src})")
                otherPlot.legend(bbox_to_anchor=(.955, 0.5), loc='center left')
        if (save):
            plt.savefig(outputName)
        if (show):
            plt.show()


if __name__ == "__main__":
    print("Which Test do you wish to run? (enter choice number)")
    print("1: sensorSim, 2: Plot Log, 3: Plot Field, 4: Util Source Isolation")
    test = ""
    while not test.isnumeric():
        test = input()

    if (test == "1"):
        sim = sensorSim("logs/field_test.csv",
                        interface="can0", dataFormat="parsed")
        try:
            sim.run()
        except KeyboardInterrupt:
            print("\n")
            sim.bus.shutdown()
            print("Replay stopped by user.")
    elif (test == "2"):
        canVis.plot_log("logs/run-data/master-run.csv", raw=False,
                        sourceType="src", asOne=False, show=True, save=False, excludeSrc=[0])
    elif (test == "3"):
        canVis.plot_NOx(file="logs/run-data/master-run.csv", raw=False,
                        sourceType="pgn", show=True, save=False, excludeSrc=[65247])
    elif (test == "4"):
        fromFile = utils.isolate_source("logs/simTest.log.csv", 0, "src")
        fromDataframe = utils.isolate_source(
            pd.read_csv("logs/simTest.log.csv"), 0, "src")
        print(fromFile)
        print(fromDataframe)
    else:
        raise IndexError("Inputted test value is invalid")
