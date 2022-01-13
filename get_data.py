# standard imports
import numpy as np
import time
import matplotlib.pyplot as plt

# local imports
from imu_dl import IMU  # TODO: Modify import path

# %% Initialize IMU communication
'''stream timing settings (microseconds)'''
interval = 10**4  # sample interval
duration = 5*10**6  # recording duration
delay = 1000  # delay before recording starts
baudrate = 115200
port = 'COM3'

my_imu = IMU(port, baudrate)

# %% Preallocate data
data_len = int(duration / interval)  # length of the data array
data = np.zeros((data_len, 13))  # IMU data array

fname = 'test' # TODO: Set as constant


# %% Data Collection
start_t = time.perf_counter()  # start time
end_t = time.perf_counter()   # end time
row = 0  # iterate through IMU data array
stop = 0  # used to break while loop

with my_imu as device:

    device.set_stream(interval, duration, delay)  # set timing parameters set above
    device.start_streaming()
    while (end_t - start_t) < duration * 10 ** -6:  # run while run time is below "duration" set
        data[row, :] = device.read_data()
        if sum(data[row, :]) == 0:
            print('Failure at row: ', row)

        row += 1

        if row == (data_len):
            print('Streaming Done!')
            break

        end_t = time.perf_counter()  # update end time

    device.stop_streaming()

# %% 
data = data[data[:, 0] > 0, :]  # Truncate zeros
np.save(fname, data)

# %%

# %% Plot Data

time_array = [(x - data[0, 0]) * 10 ** -6 for x in data[:, 0]]  # test time in seconds
units = ['rad/s', 'G', 'Norm Gauss']
titles = ['Gyroscope', 'Accelerometer', 'Magnetometer']

n_sensors = 3
plt.figure('IMU Sensors')
for i_sensor in range(n_sensors):
    plt.subplot(311 + i_sensor)
    window = [axis + 3 * i_sensor for axis in range(3, 6)]  # TODO: clean this up without magic numbers. window to cycle through sensor data
    plt.title(titles[i_sensor])
    plt.plot(time_array, data[:, window])
    plt.grid()
    plt.ylabel(units[i_sensor])
    plt.legend(['X', 'Y', 'Z'])

plt.xlabel('Time (sec)')

plt.show()