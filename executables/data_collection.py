# %%
# standard imports
import numpy as np
import time
import matplotlib.pyplot as plt
import os
import serial

# local imports
from iotools import IMU

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

'''Set serial port for IMU'''
imu_conn = serial.Serial(port, baudrate)

# %% Data Collection
start_time = time.perf_counter()
end_time = time.perf_counter()
row = 0  # iterate through IMU data array

with imu_conn as ser:

    my_imu = IMU(ser)  # initialize IMU connection

    # %% Preallocate data
    data_len = int(duration / interval)  # length of the data array
    n_pts = 14  # number of points collected from each imu TODO: use length from IMU object
    data = np.zeros((data_len, n_pts))  # IMU data array

    '''Start streaming data'''
    my_imu.set_stream(interval, duration, delay)  # set timing parameters set above
    my_imu.start_streaming()

    '''Collect data from IMU'''
    while (end_time - start_time) < duration * 10 ** -6:  # run while run time is below "duration" set

        data[row, :] = my_imu.get_data()
        row += 1
        end_time = time.perf_counter()  # update end time

    '''Stop streaming'''
    my_imu.stop_streaming()
    my_imu.software_reset()

# %% Save data
# TODO: Make data a dataframe so that each column has a title. Can use sensor names in build_cmd object
data = data[data[:, 1] > 0, :]  # Truncate zeros
np.savetxt(os.path.join('data', 'data.csv'), data, delimiter=",")

# %% Plot Data
time_array = [(timestamp - data[0, 1]) * 10 ** -6 for timestamp in data[:, 1]]  # test time in seconds

plt.figure('IMU Sensors')
plt.subplot(311)
plt.title('Gyroscope')
plt.plot(time_array, data[:, 4:7])
plt.grid()
plt.ylabel('rad/s')
plt.legend(['X', 'Y', 'Z'])

plt.subplot(312)
plt.title('Accelerometer')
plt.plot(time_array, data[:, 7:10])
plt.grid()
plt.ylabel('G')
plt.legend(['X', 'Y', 'Z'])

plt.subplot(313)
plt.title('Magnetometer')
plt.plot(time_array, data[:, 10:13])
plt.grid()
plt.ylabel('Norm Gauss')
plt.legend(['X', 'Y', 'Z'])

plt.xlabel('Time (sec)')

plt.show()
