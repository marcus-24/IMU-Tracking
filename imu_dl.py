import numpy as np
import serial
import struct
import time

# %% Code Summary

# %% Constant command variables
# Define stream variables
slots = struct.pack('BBBBBBBBB', 0x50, 0xfa, 0x26, 0x27, 0x23, 0x2B, 0xff, 0xff, 0xff)  # streaming slots for selected data
setResponseHead = b'\xdd' + struct.pack('>I', 0x43)
RightH_axis = struct.pack('BB', 0x74, 1)
start_stream = struct.pack('BB', 0x55, 0x55)
stop_stream = struct.pack('BB', 0x56, 0x56)
reset = struct.pack('B', 0xe2)

class IMU(serial.Serial):

    def __init__(self,
                 port,
                 baudrate):
        super().__init__(port, baudrate)  # TODO: add keyword arguments needed
	 			 
    @staticmethod
    def _checksum(cmd: bytes) -> bytes:
        """Calculates the checksum that needs to be sent with a command.
        Args:
            cmd (bytes): The command sent to the IMU as a byte.
        Returns:
            bytes: checksum that will be appended to the command.
        """
        chksum = bytes([sum(cmd) % 256])  # TODO: see if list is needed
        return chksum

    def _com_write(self,
                   cmd: bytes,
                   resp_head: bool = True) -> bytes:
        """Writes and sends a command to the IMU.
        Args:
            cmd (bytes): command that will be sent to the IMU.
            resp_head (bool, optional): Appended response header for command. Defaults to True.
        """

        chksum = self._checksum(cmd)

        if resp_head:  # If you would like to use the response header for the data
            final_cmd = b'\xf9' + cmd + chksum

        else:
            final_cmd = b'\xf7' + cmd + chksum

        self.write(final_cmd)  # TODO: Add optional output for checksum

    def software_reset(self) -> None:
        """Resets the software settings on the IMU.
        """
        print('---------------------------------------')
        print('Software reset for port', self.port)
        self.com_write(self.ser, reset, resp_head=False)
        print('paused to reinitialize sensor')
        time.sleep(0.5)

    def _flush(self) -> None:
        """[summary]
        """
        self.flushInput()
        self.flushOutput()
        print('---------------------------------------')
        print('Buffer cleared for ', self._port)


    def set_stream(self, interval: int, duration: int, delay: int) -> None:
        """[summary]

        Args:
            interval (int): [description]
            duration (int): [description]
            delay (int): [description]
        """

        print('---------------------------------------')
        print('Stream setup for port', self._port)
        self._com_write(setResponseHead, resp_head=False)
        print('write response header')

        print('Setting Right Hand Coordinate system')
        self._com_write(RightH_axis)
        check = self.read(6)
        print('Success/Failure:', check[0])

        print('Setting up streaming slots')
        self._com_write(slots)
        check = self.read(6)
        print('Success/Failure:', check[0])

        print('Applying time settings')
        timing = struct.pack('>III', interval, duration, delay)
        stream_timing = b'\x52' + timing
        self._com_write( stream_timing)
        check = self.read(6)
        print('Success/Failure:', check[0])

    def start_streaming(self) -> None:
        """Start streaming the IMU with the settings defined in the set_stream function
        """
        print('---------------------------------------')
        print('Start stream for port ', self.port)
        self._com_write(start_stream)
        check = self.read(6)
        print('Success/Failure:', check[0])

    def stop_streaming(self):
        """
        Stop streaming the IMU.
        """
        print('---------------------------------------')
        print('Stop stream for port ',self.port)
        self._com_write(stop_stream)
        check = self.read(6)
        print('Success/Failure:', check[0])

    def read_data(self) -> np.ndarray:
        """[summary]

        Returns:
            np.ndarray: [description]
        """
        raw_data = self.read(47)  # Make this more dynamic with length
        timing = struct.unpack('>I', raw_data[1:5])
        gyro = struct.unpack('>3f', raw_data[7:19])
        acc = struct.unpack('>3f', raw_data[19:31])
        mag = struct.unpack('>3f', raw_data[31:43])
        temp = struct.unpack('>f', raw_data[43:])

        # data=[t,imu #,button,gx,gy,gz,ax,ay,az,mx,my,mz,temp]
        data = [timing[0], int(self.port[-1]), raw_data[6], *gyro,
                *acc, *mag, temp[0]]  # TODO: convert to numpy array

        if raw_data[0] == 0:
            return data
        else:
            return np.zeros(13)
