# IMU-Tracking
<img src=https://img.shields.io/badge/Python-3.10.2-brightgreen\> ![GitHub last commit](https://img.shields.io/github/last-commit/marcus-24/IMU-Tracking)
## Objective 
This repository focuses on demonstrating techniques to track kinematics from inertial measurement units (IMUs).

## Setup
To keep the python modules consistent between users, the `imu_env` python environment can be downloaded via conda using the following command:

`conda env create -f environment.yml`

This installs the python modules from the conda channels and the local modules (i.e.: iotools) from the setup.py file.

## IMU Data Collection

The plot shown below was generated using the "executables/data_collection.py" script while an IMU was placed on a rotating stool for 20 seconds.

<img  src="Rotating IMU.png" align="center"/>

<br/>
The end goal will be to generate the cartesian trajectory of the IMU relative to the global earth frame and minimize the sensor drift and noise as much as possible. State estimation algorithms such as the Extended Kalman Filter can be used to reduce the trajectory error.

More to come soon!

## References

- Yost Labs Bluetooth Manual: https://yostlabs.com/wp/wp-content/uploads/pdf/3-Space-Sensor-Users-Manual-Bluetooth-1.pdf
