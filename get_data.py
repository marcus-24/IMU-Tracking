# standard imports
import numpy as np
import time
import matplotlib.pyplot as plt
import os

# local imports
from iotools import IMU

# %% Initialize IMU communication
'''stream timing settings (microseconds)'''
interval = 10**4  # sample interval
duration = 5*10**6  # recording duration
delay = 1000  # delay before recording starts
baudrate = 115200
port = 'COM4'

my_imu = IMU(port, baudrate)

# %% Preallocate data
data_len = int(duration / interval)  # length of the data array
data = np.zeros((data_len, 13))  # IMU data array

# %% Data Collection
start_t = time.perf_counter()  # start time
end_t = time.perf_counter()   # end time
row = 0  # iterate through IMU data array

with my_imu as device:

    device.set_stream(interval, duration, delay)  # set timing parameters set above
    device.start_streaming()

    while (end_t - start_t) < duration * 10 ** -6:  # run while run time is below "duration" set

        data[row, :] = device.read_data()
        row += 1
        end_t = time.perf_counter()  # update end time

    device.stop_streaming()
    device.software_reset()

# %% Save data

data = data[data[:, 0] > 0, :]  # Truncate zeros
np.savetxt(os.path.join('data', 'data.csv'), data, delimiter=",")


# %% Plot Data

time_array = [(timestamp - data[0, 0]) * 10 ** -6 for timestamp in data[:, 0]]  # test time in seconds
units = ['rad/s', 'G', 'Norm Gauss']
titles = ['Gyroscope', 'Accelerometer', 'Magnetometer']


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