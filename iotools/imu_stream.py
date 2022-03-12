# standard imports
import numpy as np
import serial
import struct
import time
from typing import Optional

# local imports
from iotools.build_cmd import BuildCommands

# %% Code Summary

"""The IMU class provides the functions needed to connect and execute commands on the bluetooth IMU.
"""

# %% Constant command variables
# Define stream variables
RightH_axis = struct.pack('BB', 0x74, 1)
START_STREAM = struct.pack('BB', 0x55, 0x55)
STOP_STREAM = struct.pack('BB', 0x56, 0x56)
RESET = struct.pack('B', 0xe2)


class IMU:
    # TODO: refactor into composition class tha uses serial. This way I dont not have to call self.read and self.write
    # https://www.geeksforgeeks.org/inheritance-and-composition-in-python/

    def __init__(self,
                 ser: serial.Serial,
                 cmd_builder: BuildCommands = BuildCommands()):
        self._ser = ser
        self._cmd_builder = cmd_builder

    def _com_write(self,
                   cmd: bytes,
                   resp_head: bool = True) -> Optional[bytes]:
        """Writes and sends a command to the IMU.
        Args:
            cmd (bytes): command that will be sent to the IMU.
            resp_head (bool, optional): Appended response header for command. Defaults to True.
        Returns:
            Optional[bytes]: checksum used to check command
        """

        chksum = bytes([sum(cmd) % 256])

        if resp_head:  # If you would like to use the response header for the data
            final_cmd = b'\xf9' + cmd + chksum

        else:
            final_cmd = b'\xf7' + cmd + chksum

        self._ser.write(final_cmd)

        chksum_len = 6  # length of returned checksum 
        return self._ser.read(chksum_len) if resp_head else None

    def software_reset(self) -> None:
        """Resets the software settings on the IMU.
        """
        print('---------------------------------------')
        print('Software reset for port', self._ser.port)
        self._com_write(RESET, resp_head=False)
        print('paused to reinitialize sensor')
        time.sleep(0.5)

    def set_stream(self, interval: int, duration: int, delay: int) -> None:
        """Set streaming settings for the IMU.
        Args:
            interval (int): interval between data points (microseconds)
            duration (int): the duration of the streaming session (microseconds)
            delay (int): the delay before the data streaming starts (microseconds)
        """

        print('---------------------------------------')
        print('Stream setup for port', self._ser.port)
        self._com_write(self._cmd_builder.pack_response_header(), resp_head=False)
        print('write response header')

        print('Setting Right Hand Coordinate system')
        check = self._com_write(RightH_axis)
        print('Success/Failure:', check[0])

        print('Setting up streaming slots')
        check = self._com_write(self._cmd_builder.pack_data_commands())
        print('Success/Failure:', check[0])

        print('Applying time settings')
        timing = struct.pack('>III', interval, duration, delay)
        stream_timing = struct.pack('B', 0x52) + timing  # TODO: look into combining this w/ top command
        check = self._com_write(stream_timing)
        print('Success/Failure:', check[0])

    def start_streaming(self) -> None:
        """Start streaming the IMU with the settings defined in the set_stream function
        """
        print('---------------------------------------')
        print('Start stream for port ', self._ser.port)
        check = self._com_write(START_STREAM)
        print('Success/Failure:', check[0])

    def stop_streaming(self):
        """Stop streaming the IMU.
        """
        print('---------------------------------------')
        print('Stop stream for port ', self._ser.port)
        check = self._com_write(STOP_STREAM)
        print('Success/Failure:', check[0])

    # def read_response_header(self) -> np.ndarray:

    def read_data(self) -> np.ndarray:
        """Function used to read data for each interval during streaming.
        Returns:
            np.ndarray: row of data points for that interval
        """

        '''Get number of bytes from data return'''
        raw_data = self._ser.read(self._cmd_builder.num_bytes)
        # TODO: convert >3f to f and >I to "idk yet" 
        # so struct.unpack(iffffffffffffff, raw_data[1:])
        suc_fail = raw_data[0]
        timing = struct.unpack('>I', raw_data[1:5])  # timestamps
        data_len = raw_data[5]
        button_press = raw_data[6]
        gyro = struct.unpack('>3f', raw_data[7:19])  # gyroscope xyz axes
        acc = struct.unpack('>3f', raw_data[19:31])  # accelerometer xyz axes
        mag = struct.unpack('>3f', raw_data[31:43])  # magnetometer xyz axes
        temp = struct.unpack('>f', raw_data[43:])  # temperature sensor

        # data=[t, imu #, button state, gx, gy, gz, ax, ay, az, mx, my, mz, temp]
        data = np.array([timing[0], int(self._ser.port[-1]), button_press, *gyro,
                         *acc, *mag, temp[0]])

        return data if raw_data[0] == 0 else np.zeros(len(data))  # return data if success bit in checksum is 0 else return zero array
