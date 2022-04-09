# standard imports
import numpy as np
import serial
from struct import pack, unpack_from
import time
from typing import Tuple

# local imports
from iotools.build_cmd import BuildCommands, CmdType

# %% Code Summary
"""The IMU class provides the functions needed to connect and execute commands on the bluetooth IMU.
"""

# %% Constant command variables
# Define stream variables
RIGHT_AXIS = pack('BB', 116, 1)
SET_STREAM = pack('B', 82)
START_STREAM = pack('BB', 85, 85)
STOP_STREAM = pack('BB', 86, 86)
RESET = pack('B', 226)


class IMU:

    def __init__(self,
                 ser: serial.Serial,
                 bldg_cmd: BuildCommands = BuildCommands()):
        self._ser = ser
        self._bldg_cmd = bldg_cmd

    def _com_write(self, cmd: bytes, msg: str, resp_head: bool = True):
        """Writes and sends a command to the IMU.
        Args:
            cmd (bytes): command that will be sent to the IMU.
            resp_head (bool, optional): Appended response header for command. Defaults to True.
        Returns:
            Optional[bytes]: checksum used to check command"""

        print(msg)
        checksum = bytes([sum(cmd) % 256])  # create checksum for command

        '''Write final command to send to imu'''
        if resp_head:  # If you would like to use the response header for the data
            final_cmd = b'\xf9' + cmd + checksum
        else:
            final_cmd = b'\xf7' + cmd + checksum

        self._ser.write(final_cmd)  # send command to imu

        '''Print checksum from response header'''
        if resp_head:
            check = self._ser.read(self._bldg_cmd.resp_num_bytes)
            print('Success/Failure:', check[0])

    def software_reset(self) -> None:
        """Resets the software settings on the IMU."""
        print('---------------------------------------')
        self._com_write(RESET, msg=f'Software reset for port {self._ser.port}', resp_head=False)
        time.sleep(0.5)

    def set_stream(self, interval: int, duration: int, delay: int) -> None:
        """Set streaming settings for the IMU.
        Args:
            interval (int): interval between data points (microseconds)
            duration (int): the duration of the streaming session (microseconds)
            delay (int): the delay before the data streaming starts (microseconds)"""

        print('---------------------------------------')
        print('Stream setup for port', self._ser.port)
        self._com_write(self._bldg_cmd.pack_response_header(),
                        msg='write response header',
                        resp_head=False)

        self._com_write(RIGHT_AXIS, msg='Setting Right Hand Coordinate system')

        self._com_write(self._bldg_cmd.pack_data_cmds(), msg='Setting up streaming slots')

        timing = SET_STREAM + pack('>III', interval, duration, delay)
        self._com_write(timing, msg='Applying time settings')

    def start_streaming(self) -> None:
        """Start streaming the IMU with the settings defined in the set_stream function"""
        print('---------------------------------------')
        self._com_write(START_STREAM, msg=f'Start stream for port {self._ser.port}')

    def stop_streaming(self) -> None:
        """Stop streaming the IMU."""
        print('---------------------------------------')
        self._com_write(STOP_STREAM, msg=f'Stop stream for port {self._ser.port}')

    def _read_bytes(self,
                    raw_data: bytes,
                    bytes_read: int,
                    commands: CmdType) -> Tuple[np.ndarray, int]:
        """Reads raw bytes returned from the IMU and unpacks them into readable data
        Args:
            raw_data (bytes): raw data from IMU
            bytes_read (int): number of bytes that have been read from bytes array so far
            commands (CmdType): IMU commands to read and unpack

        Returns:
            Tuple[np.ndarray, int]: parsed data and the updated bytes_read
        """

        parsed_data = list()
        for _, cmd in commands.items():  # cycle through selected commands
            if "unpack" in cmd.keys():  # if data needs to be unpacked
                parsed_data.extend(unpack_from(cmd['unpack'], raw_data, offset=bytes_read))
            else:  # if you can read data as is
                parsed_data.append(raw_data[bytes_read])
            bytes_read += cmd['raw length']
                
        return parsed_data, bytes_read

    def get_data(self) -> np.ndarray:
        """Function used to read data for each interval during streaming.
        Returns:
            np.ndarray: row of data points for that interval"""

        '''Get number of bytes from data return'''
        raw_data = self._ser.read(self._bldg_cmd.total_num_bytes)

        '''Read data from IMU byte array'''
        bytes_read = 0  # number of bytes read so far in buffer
        parsed_resp, bytes_read = self._read_bytes(raw_data, bytes_read, self._bldg_cmd.resp_cmds)  # read response header
        parsed_data, _ = self._read_bytes(raw_data, bytes_read, self._bldg_cmd.data_cmds)  # read imu data
        data = parsed_resp + parsed_data  # combine data into one array

        # TODO: account for when success bit is not the first header (Write into dataframe)
        return data if raw_data[0] == 0 else np.zeros(len(data))  # return data if success bit in checksum is 0 else return zero array
