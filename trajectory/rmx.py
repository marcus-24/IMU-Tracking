import numpy as np
import math as mt
import numpy.linalg as mx
from typing import List


def initial_quaternion(acc_avg: np.ndarray, psi: float) -> List[float]:
    """Calculate intial quaternion
    Args:
        acc_avg (np.ndarray): average accelerometer values
        psi (float): psi angle
    Returns:
        List[float]: inital quaternion vector
    """

    '''Compile accelerometer values'''
    ax_avg = -acc_avg[0]
    ay_avg = -acc_avg[1]
    az_avg = -acc_avg[2]

    '''Get initial euler angles'''
    theta = mt.atan(ax_avg / mt.sqrt((ay_avg**2) + (az_avg**2)))

    phi = mt.atan(ay_avg / az_avg)
    if az_avg > 0:
        if ay_avg > 0:
            phi -= mt.pi
        elif ay_avg < 0:
            phi += mt.pi

    '''Calculate initial quaternion'''
    q0_int = mt.cos(psi / 2) * mt.cos(theta / 2) * mt.cos(phi / 2) + mt.sin(psi / 2) * mt.sin(theta / 2) * mt.sin(phi / 2)
    q1_int = mt.cos(psi / 2) * mt.cos(theta / 2) * mt.sin(phi / 2) - mt.sin(psi / 2) * mt.sin(theta / 2) * mt.cos(phi / 2)
    q2_int = mt.cos(psi / 2) * mt.sin(theta / 2) * mt.cos(phi / 2) + mt.sin(psi / 2) * mt.cos(theta / 2) * mt.sin(phi / 2)
    q3_int = mt.sin(psi / 2) * mt.cos(theta / 2) * mt.cos(phi / 2) - mt.cos(psi / 2) * mt.sin(theta / 2) * mt.sin(phi / 2)

    Norm = mx.norm([q0_int, q1_int, q2_int, q3_int])

    Q_int = [q0_int/Norm, q1_int/Norm, q2_int/Norm, q3_int/Norm]

    return Q_int


def instant_quaternion(gyro: np.ndarray, quat0: np.ndarray, dt: float) -> np.ndarray:
    """Generate instantaneous quaternion vector
    Args:
        gyro ([type]): angular velocity from gyroscope
        quat0 (np.ndarray): previous quaternion vector
        dt (float): sample interval
    Returns:
        np.ndarray: instantaneous quaternion
    """
    omega = np.array([[2, -gyro[0]*dt, -gyro[1]*dt, -gyro[2]*dt],
                      [gyro[0]*dt, 2, gyro[2]*dt, -gyro[1]*dt],
                      [gyro[1]*dt, -gyro[2]*dt, 2, gyro[0]*dt],
                      [gyro[2]*dt, gyro[1]*dt, -gyro[0]*dt, 2]])

    instQuat = 0.5 * np.dot(omega, quat0)
    instQuat /= mx.norm(instQuat)

    return instQuat


def quat2rmx(quat: np.ndarray) -> np.ndarray:
    """Convert quaternion to rotation matrix.
    Args:
        quat (np.ndarray): quaternion vector
    Returns:
        np.ndarray: rotation matrix
    """
    q02 = quat[0]**2
    q12 = quat[1]**2
    q22 = quat[2]**2
    q32 = quat[3]**2

    rot_mx = np.array([[2*q02-1+2*q12, 2*quat[1]*quat[2]-2*quat[0]*quat[3], 2*quat[1]*quat[3]+2*quat[0]*quat[2]],
                       [2*quat[1]*quat[2]+2*quat[0]*quat[3], 2*q02-1+2*q22, 2*quat[2]*quat[3]-2*quat[0]*quat[1]],
                       [2*quat[1]*quat[3]-2*quat[0]*quat[2], 2*quat[2]*quat[3]+2*quat[0]*quat[1], 2*q02-1+2*q32]])
    return rot_mx


def global_acc(rot_mx: np.ndarray, acc: np.ndarray) -> np.ndarray:
    """transform IMU acceleration to global acceleration.
    Args:
        rot_mx (np.ndarray): IMU to global rotation matrix
        acc (np.ndarray): acceleration in the IMU frame
    Returns:
        np.ndarray: acceleration in the global frame
    """
    acc_trans = np.transpose(acc)
    gravity = np.transpose([0, 0, 1])
    glob_acc = np.transpose((np.dot(rot_mx, acc_trans) - gravity)) * 9.81  # convert to m/s^2

    return glob_acc

# TODO: replace trapz with scipy trapezoidal integration

def heading_angle(mag: np.ndarray) -> float:
    """Get heading angle from magnetometer
    Args:
        mag (np.ndarray): normalized magnetometer vector
    Returns:
        float: heading angle
    """
    yaw = mt.atan2(mag[1], mag[0])
    if yaw < 0:
        yaw += 2 * np.pi

    return yaw


def rmx2eul(rot_mx: np.ndarray) -> np.ndarray:
    """convert rotation matrix to euler angles
    Args:
        rot_mx (np.ndarray): IMU to global rotation matrix
    Returns:
        np.ndarray: vector of euler angles
    """
    n_angles = 3  # number of euler angles
    eul = np.zeros(n_angles)
    eul[0] = mt.atan2(rot_mx[1, 2], rot_mx[2, 2])
    eul[1] = mt.atan2(-rot_mx[0, 2], mx.norm(rot_mx[0, 0:2]))
    eul[2] = mt.atan2(rot_mx[0, 1], rot_mx[0, 0])

    return eul
