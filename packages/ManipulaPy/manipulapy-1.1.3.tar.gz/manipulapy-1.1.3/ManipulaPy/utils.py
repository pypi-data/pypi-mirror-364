#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Utilities Module - ManipulaPy

This module contains essential utility functions for working with rigid body motions,
transformations, and related operations in robotic manipulation. Functions cover
screw theory, matrix operations, Lie algebra computations, time scaling, and
coordinate transformations for kinematics and dynamics calculations.

The functions in this module support:
- Extracting and manipulating screw vectors and twists
- Computing transformation matrices from twists and joint angles
- Matrix logarithms and exponentials for SE(3) and SO(3)
- Converting between rotation matrices and Euler angles
- Skew-symmetric matrix operations
- Time scaling functions for trajectory generation

Copyright (c) 2025 Mohamed Aboelnasr

This file is part of ManipulaPy.

ManipulaPy is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

ManipulaPy is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with ManipulaPy. If not, see <https://www.gnu.org/licenses/>.
"""

import numpy as np
from scipy.linalg import expm


def extract_r_list(Slist):
    """
    Extracts the r_list from the given Slist.

    Parameters:
        Slist (list): A list of S vectors representing the joint screws.

    Returns:
        np.ndarray: An array of r vectors.
    """
    # Handle None or improperly shaped input
    if Slist is None or not hasattr(np.array(Slist), "T"):
        return np.array([])

    # Continue with the original function
    r_list = []
    for S in np.array(Slist).T:
        omega = S[:3]
        v = S[3:]
        if np.linalg.norm(omega) != 0:
            r = -np.cross(omega, v) / np.linalg.norm(omega) ** 2
            r_list.append(r)
        else:
            r_list.append([0, 0, 0])  # For prismatic joints
    return np.array(r_list)


def extract_omega_list(Slist):
    """
    Extracts the first three elements from each sublist in the given list and returns them as a numpy array.

    Parameters:
        Slist (list): A list of sublists.

    Returns:
        np.array: A numpy array containing the first three elements from each sublist.
    """
    return np.array(Slist)[:, :3]

def extract_screw_list(omega_list, r_list):
    """
    Build a 6xn screw-axis matrix from (3xn) angular velocities 'omega_list'
    and (3xn) positions 'r_list'.
    For each column i:
       S[:3, i] = w = omega_list[:, i]
       S[3:, i] = v = - w x r

    Returns a 6xn array of [wx, wy, wz, vx, vy, vz] in each column.
    """
    if omega_list is None or r_list is None:
        return None

    # Convert to numpy arrays if not already
    omega_list = np.asarray(omega_list)
    r_list = np.asarray(r_list)
    
    # Handle case where r_list is empty or 1D
    if r_list.size == 0:
        # Create a default r_list with zeros
        if omega_list.ndim == 2:
            n_joints = omega_list.shape[1]
        else:
            n_joints = omega_list.shape[0] // 3 if omega_list.ndim == 1 else 1
        r_list = np.zeros((3, n_joints))
    elif r_list.ndim == 1:
        # If r_list is 1D, reshape or handle appropriately
        if r_list.size == 0:
            if omega_list.ndim == 2:
                n_joints = omega_list.shape[1]
            else:
                n_joints = 1
            r_list = np.zeros((3, n_joints))
        elif r_list.size == 3:
            # Single position vector, reshape to (3, 1)
            r_list = r_list.reshape(3, 1)
        else:
            # Multiple positions in 1D array, try to reshape
            if r_list.size % 3 == 0:
                n_positions = r_list.size // 3
                r_list = r_list.reshape(3, n_positions)
            else:
                raise ValueError(f"Cannot reshape r_list of size {r_list.size} into (3, n) format")

    # Ensure omega_list is also 2D
    if omega_list.ndim == 1:
        if omega_list.size % 3 == 0:
            n_joints = omega_list.size // 3
            omega_list = omega_list.reshape(3, n_joints)
        else:
            raise ValueError(f"Cannot reshape omega_list of size {omega_list.size} into (3, n) format")

    w_rows, w_cols = omega_list.shape
    r_rows, r_cols = r_list.shape
    
    if w_rows != 3 or r_rows != 3:
        raise ValueError("omega_list and r_list must each have 3 rows.")
    if w_cols != r_cols:
        # Try to broadcast if one has only one column
        if r_cols == 1 and w_cols > 1:
            r_list = np.tile(r_list, (1, w_cols))
            r_cols = w_cols
        elif w_cols == 1 and r_cols > 1:
            omega_list = np.tile(omega_list, (1, r_cols))
            w_cols = r_cols
        else:
            raise ValueError(f"omega_list and r_list must have the same number of columns. Got {w_cols} and {r_cols}.")

    S = np.zeros((6, w_cols), dtype=float)
    for i in range(w_cols):
        w = omega_list[:, i]
        r = r_list[:, i]
        v = np.cross(-w, r)
        S[:3, i] = w
        S[3:, i] = v
    return S


def NearZero(z):
    """
    Determines if a given number is near zero.

    Parameters:
        z (float): The number to check.

    Returns:
        bool: True if the number is near zero, False otherwise.
    """
    return abs(z) < 1e-6


def skew_symmetric(v):
    """
    Returns the skew symmetric matrix of a 3D vector.

    Parameters:
        v (array-like): A 3D vector.

    Returns:
        np.ndarray: The corresponding skew symmetric matrix.
    """
    return np.array([[0, -v[2], v[1]], [v[2], 0, -v[0]], [-v[1], v[0], 0]])


def transform_from_twist(S, theta):
    """
    Computes the transformation matrix from a twist and a joint angle.

    Parameters:
        S (array-like): A 6D twist vector.
        theta (float): The joint angle.

    Returns:
        np.ndarray: The corresponding transformation matrix.
    """
    omega = S[:3]
    v = S[3:]
    if np.linalg.norm(omega) == 0:  # Prismatic joint
        return np.vstack((np.eye(3), v * theta)).T
    else:  # Revolute joint
        skew_omega = skew_symmetric(omega)
        R = (
            np.eye(3)
            + np.sin(theta) * skew_omega
            + (1 - np.cos(theta)) * np.dot(skew_omega, skew_omega)
        )
        p = np.dot(
            np.eye(3) * theta
            + (1 - np.cos(theta)) * skew_omega
            + (theta - np.sin(theta)) * np.dot(skew_omega, skew_omega),
            v,
        )
        return np.vstack((np.hstack((R, p.reshape(-1, 1))), [0, 0, 0, 1]))


def adjoint_transform(T):
    """
    Computes the adjoint transformation matrix for a given transformation matrix.

    Parameters:
        T (np.ndarray): A 4x4 transformation matrix.

    Returns:
        np.ndarray: The corresponding adjoint transformation matrix.
    """
    R = T[0:3, 0:3]
    p = T[0:3, 3]
    skew_p = skew_symmetric(p)
    return np.vstack((np.hstack((R, np.zeros((3, 3)))), np.hstack((skew_p @ R, R))))


def logm(T):
    """
    Computes the logarithm of a transformation matrix.

    Parameters:
        T (np.ndarray): A 4x4 transformation matrix.

    Returns:
        np.ndarray: The logarithm of the transformation matrix.
    """
    R = T[0:3, 0:3]
    p = T[0:3, 3]
    omega, theta = rotation_logm(R)
    if np.linalg.norm(omega) < 1e-6:
        v = p / theta
    else:
        G_inv = (
            1 / theta * np.eye(3)
            - 0.5 * skew_symmetric(omega)
            + (1 / theta - 0.5 / np.tan(theta / 2))
            * np.dot(skew_symmetric(omega), skew_symmetric(omega))
        )
        v = np.dot(G_inv, p)
    return np.hstack((omega * theta, v))


def rotation_logm(R):
    """
    Computes the logarithm of a rotation matrix.

    Parameters:
        R (np.ndarray): A 3x3 rotation matrix.

    Returns:
        tuple: A tuple containing the rotation vector and the angle.
    """
    theta = np.arccos((np.trace(R) - 1) / 2)
    if theta < 1e-6:
        return np.zeros(3), theta
    else:
        omega = (
            1
            / (2 * np.sin(theta))
            * np.array([R[2, 1] - R[1, 2], R[0, 2] - R[2, 0], R[1, 0] - R[0, 1]])
        )
        return omega, theta


def logm_to_twist(logm):
    """
    Convert the logarithm of a transformation matrix to a twist vector.

    Parameters:
        logm (np.ndarray): The logarithm of a transformation matrix.

    Returns:
        np.ndarray: The corresponding twist vector.
    """
    if logm.shape != (4, 4):
        raise ValueError("logm must be a 4x4 matrix.")

    omega_matrix = logm[0:3, 0:3]
    omega = skew_symmetric_to_vector(omega_matrix)
    v = logm[0:3, 3]
    return np.hstack((omega, v))


def skew_symmetric_to_vector(skew_symmetric):
    """
    Convert a skew-symmetric matrix to a vector.

    Parameters:
        skew_symmetric (np.ndarray): A 3x3 skew-symmetric matrix.

    Returns:
        np.ndarray: The corresponding vector.
    """
    return np.array([skew_symmetric[2, 1], skew_symmetric[0, 2], skew_symmetric[1, 0]])


def se3ToVec(se3_matrix):
    """
    Convert an se(3) matrix to a twist vector.

    Parameters:
        se3_matrix (np.ndarray): A 4x4 matrix from the se(3) Lie algebra.

    Returns:
        np.ndarray: A 6-dimensional twist vector.
    """
    if se3_matrix.shape != (4, 4):
        raise ValueError("Input matrix must be a 4x4 matrix.")

    omega = np.array([se3_matrix[2, 1], se3_matrix[0, 2], se3_matrix[1, 0]])
    v = se3_matrix[0:3, 3]
    return np.hstack((omega, v))


def TransToRp(T):
    """
    Converts a homogeneous transformation matrix into a rotation matrix and position vector.

    Parameters:
        T (np.ndarray): A 4x4 transformation matrix.

    Returns:
        tuple: A tuple containing the rotation matrix and position vector.
    """
    R = T[0:3, 0:3]
    p = T[0:3, 3]
    return R, p


def TransInv(T):
    """
    Inverts a homogeneous transformation matrix.

    Parameters:
        T (np.ndarray): A 4x4 transformation matrix.

    Returns:
        np.ndarray: The inverse of the transformation matrix.
    """
    R, p = TransToRp(T)
    Rt = R.T
    return np.vstack((np.hstack((Rt, -Rt @ p.reshape(-1, 1))), [0, 0, 0, 1]))


def MatrixLog6(T):
    """
    Compute the matrix logarithm of a given transformation matrix T.

    Parameters:
        T (np.ndarray): The transformation matrix of shape (4, 4).

    Returns:
        np.ndarray: The matrix logarithm of T, with shape (4, 4).
    """
    R, p = TransToRp(T)
    omega, theta = rotation_logm(R)
    if np.linalg.norm(omega) < 1e-6:
        return np.vstack(
            (np.hstack((np.zeros((3, 3)), p.reshape(-1, 1))), [0, 0, 0, 0])
        )
    else:
        omega_mat = skew_symmetric(omega)
        G_inv = (
            1 / theta * np.eye(3)
            - 0.5 * omega_mat
            + (1 / theta - 0.5 / np.tan(theta / 2)) * omega_mat @ omega_mat
        )
        v = G_inv @ p
        return np.vstack((np.hstack((omega_mat, v.reshape(-1, 1))), [0, 0, 0, 0]))


def MatrixExp6(se3mat):
    """
    Computes the matrix exponential of a matrix in se(3).

    Parameters:
        se3mat (np.ndarray): A 4x4 matrix representing a twist in se(3).

    Returns:
        np.ndarray: The corresponding 4x4 transformation matrix in SE(3).
    """
    if se3mat.shape != (4, 4):
        raise ValueError("Input matrix must be of shape (4, 4)")

    omega = np.array([se3mat[2, 1], se3mat[0, 2], se3mat[1, 0]])
    v = np.array([se3mat[0, 3], se3mat[1, 3], se3mat[2, 3]])
    omega_magnitude = np.linalg.norm(omega)

    if omega_magnitude < 1e-6:
        return np.eye(4) + se3mat

    omega_skew = skew_symmetric(omega)
    omega_exp = expm(omega_skew * omega_magnitude)
    omega_skew_squared = np.dot(omega_skew, omega_skew)
    v_term = (
        np.eye(3) * omega_magnitude
        + (1 - np.cos(omega_magnitude)) * omega_skew
        + (omega_magnitude - np.sin(omega_magnitude)) * omega_skew_squared
    ) / omega_magnitude**2
    v_term = np.dot(v_term, v)

    T = np.eye(4)
    T[:3, :3] = omega_exp
    T[:3, 3] = v_term

    return T


def MatrixLog3(R):
    """
    Computes the matrix logarithm of a rotation matrix.

    Parameters:
        R (np.ndarray): A 3x3 rotation matrix.

    Returns:
        np.ndarray: The matrix logarithm of the rotation matrix.
    """
    acosinput = (np.trace(R) - 1) / 2.0
    if acosinput >= 1:
        return np.zeros((3, 3))
    elif acosinput <= -1:
        if not NearZero(1 + R[2][2]):
            omega = (1.0 / np.sqrt(2 * (1 + R[2][2]))) * np.array(
                [R[0][2], R[1][2], 1 + R[2][2]]
            )
        elif not NearZero(1 + R[1][1]):
            omega = (1.0 / np.sqrt(2 * (1 + R[1][1]))) * np.array(
                [R[0][1], 1 + R[1][1], R[2][1]]
            )
        else:
            omega = (1.0 / np.sqrt(2 * (1 + R[0][0]))) * np.array(
                [1 + R[0][0], R[1][0], R[2][0]]
            )
        return VecToso3(np.pi * omega)
    else:
        theta = np.arccos(acosinput)
        return theta / 2.0 / np.sin(theta) * (R - np.array(R).T)


def VecToso3(omega):
    """
    Converts a 3D angular velocity vector to a skew-symmetric matrix.

    Parameters:
        omega (array-like): A 3D angular velocity vector.

    Returns:
        np.ndarray: The corresponding skew-symmetric matrix.
    """
    return np.array(
        [[0, -omega[2], omega[1]], [omega[2], 0, -omega[0]], [-omega[1], omega[0], 0]]
    )


def VecTose3(V):
    """
    Converts a spatial velocity vector to an se(3) matrix.

    Parameters:
        V (array-like): A 6D spatial velocity vector.

    Returns:
        np.ndarray: The corresponding 4x4 matrix in se(3).
    """
    return np.r_[np.c_[VecToso3(V[:3]), V[3:].reshape(3, 1)], np.zeros((1, 4))]


def MatrixExp3(so3mat):
    """
    Computes the matrix exponential of a matrix in so(3).

    Parameters:
        so3mat (np.ndarray): A 3x3 skew-symmetric matrix.

    Returns:
        np.ndarray: The corresponding 3x3 rotation matrix in SO(3).
    """
    return expm(so3mat)


def CubicTimeScaling(Tf, t):
    """
    Compute the cubic time scaling factor.

    Parameters:
        Tf (float): The total time of the motion.
        t (float): The current time.

    Returns:
        float: The cubic time scaling factor.
    """
    return 3 * (t / Tf) ** 2 - 2 * (t / Tf) ** 3


def QuinticTimeScaling(Tf, t):
    """
    Compute the quintic time scaling factor.

    Parameters:
        Tf (float): The total time of the motion.
        t (float): The current time.

    Returns:
        float: The quintic time scaling factor.
    """
    return 10 * (t / Tf) ** 3 - 15 * (t / Tf) ** 4 + 6 * (t / Tf) ** 5


def rotation_matrix_to_euler_angles(R):
    """
    Convert a rotation matrix to Euler angles (roll, pitch, yaw).

    Parameters:
        R (numpy.ndarray): A 3x3 rotation matrix.

    Returns:
        numpy.ndarray: A 3-element array representing the Euler angles (roll, pitch, yaw).
    """
    assert R.shape == (3, 3), f"Expected 3x3 rotation matrix, got shape {R.shape}"
    sy = np.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)

    singular = sy < 1e-6

    if not singular:
        x = np.arctan2(R[2, 1], R[2, 2])
        y = np.arctan2(-R[2, 0], sy)
        z = np.arctan2(R[1, 0], R[0, 0])
    else:
        x = np.arctan2(-R[1, 2], R[1, 1])
        y = np.arctan2(-R[2, 0], sy)
        z = 0

    return np.array([x, y, z])


def euler_to_rotation_matrix(euler_deg):
    """
    Convert Euler angles (roll_deg, pitch_deg, yaw_deg) in degrees
    to a 3x3 rotation matrix.
    ZYX convention is typical in robotics: yaw -> pitch -> roll,
    but adapt as needed.

    Parameters:
        euler_deg (array-like): [roll_deg, pitch_deg, yaw_deg]

    Returns:
        np.ndarray: A 3x3 rotation matrix (float64 by default).
    """
    roll_deg, pitch_deg, yaw_deg = euler_deg
    # Convert degrees to radians
    roll = np.radians(roll_deg)
    pitch = np.radians(pitch_deg)
    yaw = np.radians(yaw_deg)

    # Example Z-Y-X convention (yaw→pitch→roll).
    # If your code uses X→Y→Z or another sequence, adapt these multiplications.
    Rz = np.array(
        [[np.cos(yaw), -np.sin(yaw), 0], [np.sin(yaw), np.cos(yaw), 0], [0, 0, 1]],
        dtype=np.float64,
    )

    Ry = np.array(
        [
            [np.cos(pitch), 0, np.sin(pitch)],
            [0, 1, 0],
            [-np.sin(pitch), 0, np.cos(pitch)],
        ],
        dtype=np.float64,
    )

    Rx = np.array(
        [[1, 0, 0], [0, np.cos(roll), -np.sin(roll)], [0, np.sin(roll), np.cos(roll)]],
        dtype=np.float64,
    )

    # Multiply in the correct order for your convention.
    R = Rz @ Ry @ Rx
    return R
