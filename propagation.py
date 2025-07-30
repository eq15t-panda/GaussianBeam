import numpy as np
from scipy.optimize import root_scalar

from matrix import lens, free_space


def gaussian_beam_waist(w0, wavelength, *matrices):
    """
    Calculate the waist of a Gaussian beam after propagation through an optical system.

    :param w0: Initial beam waist (in meters).
    :param wavelength: Wavelength of the beam (in meters).
    :param matrices: One or more ABCD matrices representing the optical system.
    :return: Final beam waist (in meters).
    """
    # Calculate the overall ABCD matrix
    overall_matrix = np.eye(2)
    for matrix in matrices:
        overall_matrix = np.dot(overall_matrix, matrix)

    # Extract the parameters from the overall matrix
    A, B, C, D = overall_matrix.flatten()

    # Calculate the Rayleigh range
    z_r = np.pi * w0 ** 2 / wavelength

    # Initial complex beam parameter
    q = 1j * z_r  # we consider the wavefront infinite for simplicity if we take the waist in the middle of the curved mirrors
    # of a bow-tie ring cavity.

    # Apply the ABCD transformation
    q_prime = (A * q + B) / (C * q + D)

    # Calculate the new beam waist
    w_prime = np.sqrt(-wavelength / (np.pi * np.imag(1 / q)))
    # Calculate new wavefront
    R_prime = np.real(1 / q_prime)

    return w_prime, R_prime


def propagation(d_lens, w0, wavelength, roc, focal_length, d_c):
    """
    Calculate the distance d_lens for collimation and the associated beam waist.

    :param d_lens: Distance from the lens to the curved mirror (in meters).
    :param w0: Initial beam waist (in meters).
    :param wavelength: Wavelength of the beam (in meters).
    :param roc: radius of curvature (in meters).
    :param focal_length: List of focal lengths of the converging lens (in meters).
    :param d_c: Distance between the curved mirror and the origin (in meters).
    :return: Results as a dictionary with RoC and focal lengths as keys.
    """
    # Free space propagation to the curved mirror
    propagation_to_mirror = free_space(d_c / 2)
    # Calculate the focal length of the mirror
    f_mirror = -roc / 2  # Diverging lens equivalent focal length
    mirror_matrix = lens(f_mirror)

    # Lens propagation matrix and free space propagation to the lens
    lens_matrix = lens(focal_length)
    propagation_to_lens = free_space(d_lens / 2)

    # Calculate the waist and wavefront after propagation through the optical system
    # Propagation to mirror -> Mirror -> Propagation to lens -> Lens
    waist, wavefront = gaussian_beam_waist(w0, wavelength,
                                           lens_matrix,
                                           propagation_to_lens,
                                           mirror_matrix,
                                           propagation_to_mirror
                                           )

    return waist, wavefront


def find_d_lens(w0, wavelength, roc, focal_length, d_c):
    """
    Find the distance d_lens for collimation of the Gaussian beam.

    :param w0: Initial beam waist (in meters).
    :param wavelength: Wavelength of the beam (in meters).
    :param roc: Radius of curvature (in meters).
    :param focal_length: Focal length of the converging lens (in meters).
    :param d_c: Distance between the curved mirror and the origin (in meters).
    :return: Optimal distance d_lens for collimation.
    """
    result = root_scalar(lambda d_lens: propagation(d_lens, w0, wavelength, roc, focal_length, d_c)[1], bracket=(0.01, 10))
    if result.converged:
        return result.root
    else:
        raise ValueError("Root finding did not converge.")