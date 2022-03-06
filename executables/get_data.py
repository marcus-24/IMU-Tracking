# standard imports
import numpy as np
import time
import matplotlib.pyplot as plt
import os
import serial

# local imports
from iotools import IMU, BuildCommands

# %% Code Summary
"""This script is an example for how to collect data from a Yost labs
bluetooth IMU sensor and display the raw data from each sensor.
"""

# %% Initialize IMU communication
'''stream timing settings (microseconds)'''
interval = 10**4  # sample interval
duration = 20*10**6  # recording duration
delay = 1000  # delay before recording starts
baudrate = 115200
port = 'COM4'

'''Compile slot commands'''
# TODO: Look into a Creation design pattern for this
cmd_builder = BuildCommands()

'''Set serial port for IMU'''
imu_conn = serial.Serial(port, baudrate)
# %% Preallocate data
data_len = int(duration / interval)  # length of the data array
n_pts = 13  # number of points collected from each
data = np.zeros((data_len, n_pts))  # IMU data array

# %% Data Collection
start_t = time.perf_counter()  # start time
end_t = time.perf_counter()   # end time
row = 0  # iterate through IMU data array

with imu_conn as ser:

    my_imu = IMU(ser, cmd_builder)  # initialize IMU connection

    '''Start streaming data'''
    my_imu.set_stream(interval, duration, delay)  # set timing parameters set above
    my_imu.start_streaming()

    '''Collect data from IMU'''
    while (end_t - start_t) < duration * 10 ** -6:  # run while run time is below "duration" set

        data[row, :] = my_imu.read_data()
        row += 1
        end_t = time.perf_counter()  # update end time

    '''Stop streaming'''
    my_imu.stop_streaming()
    my_imu.software_reset()

# %% Save data
data = data[data[:, 0] > 0, :]  # Truncate zeros
np.savetxt(os.path.join('data', 'data.csv'), data, delimiter=",")

# %% Plot Data
time_array = [(timestamp - data[0, 0]) * 10 ** -6 for timestamp in data[:, 0]]  # test time in seconds

plt.figure('IMU Sensors')
plt.subplot(311)
plt.title('Gyroscope')
plt.plot(time_array, data[:, 3:6])
plt.grid()
plt.ylabel('rad/s')
plt.legend(['X', 'Y', 'Z'])

plt.subplot(312)
plt.title('Accelerometer')
plt.plot(time_array, data[:, 6:9])
plt.grid()
plt.ylabel('G')
plt.legend(['X', 'Y', 'Z'])

plt.subplot(313)
plt.title('Magnetometer')
plt.plot(time_array, data[:, 9:12])
plt.grid()
plt.ylabel('Norm Gauss')
plt.legend(['X', 'Y', 'Z'])

plt.xlabel('Time (sec)')

plt.show()
