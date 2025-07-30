import numpy as np


def lens(focal_length):
    """
    ABCD matrix for a thin lens of focal length `focal_length`. For a mirror with radius of curvature R, the focal
    length is given by f = R/2.
    :param focal_length:
    :return:
    """
    return np.array([[1, 0], [-1 / focal_length, 1]])


def free_space(distance):
    """
    ABCD matrix for free space propagation over a distance `distance`.
    :param distance:
    :return:
    """
    return np.array([[1, distance], [0, 1]])


