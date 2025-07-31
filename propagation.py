import csv
import numpy as np
from scipy.optimize import root_scalar
import os

from matrix import lens, free_space
from utils import csv_utils as csvu


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
    # print(overall_matrix)

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
    w_prime = np.sqrt(-wavelength / (np.pi * np.imag(1 / q_prime)))
    # print(w_prime)
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


def find_d_lens(w0, wavelength, roc, focal_length, d_curved):
    """
    Find the distance d_lens for collimation of the Gaussian beam.

    :param w0: Initial beam waist (in meters).
    :param wavelength: Wavelength of the beam (in meters).
    :param roc: Radius of curvature (in meters).
    :param focal_length: Focal length of the converging lens (in meters).
    :param d_curved: Distance between the curved mirror and the origin (in meters).
    :return: Optimal distance d_lens for collimation.
    """
    result = root_scalar(lambda d_lens: propagation(d_lens, w0, wavelength, roc, focal_length, d_curved)[1],
                         bracket=(0.01, 10))
    if result.converged:
        return result.root
    else:
        raise ValueError("Root finding did not converge.")


if __name__ == "__main__":
    # Set wavelength for pump and harmonic
    pump = 780e-9
    harmonic = pump / 2

    # Set initial beam waist
    w_blu_opo = 30e-6  # 40 microns
    w_red_opo = w_blu_opo / np.sqrt(2)

    # Set radii of curvature and focal lengths
    ROC = np.array([100, 150]) * 1e-3  # 100 mm and 150 mm
    f = np.array([50, 75, 100, 200, 300, 400, 500]) * 1e-3  # 50 mm to 500 mm

    # Set distance between curved mirror and origin
    d_c = 125e-3 / 2  # 125 mm divided by 2 is the typical distance found between curved mirrors in a bow-tie ring cavity

    csvu.ensure_header()
    existing = csvu.read_existing_results()

    for roc in ROC:
        for focal_length in f:
            try:
                d_lens_root = find_d_lens(w_blu_opo, pump, roc, focal_length, d_c)
                waist, wavefront = propagation(d_lens_root, w_blu_opo, harmonic, roc, focal_length, d_c)

                key = (w_blu_opo * 1e6, roc * 1e3, focal_length * 1e3, d_lens_root * 1e3)
                if key not in existing:
                    csvu.append_result(w_blu_opo * 1e6, roc * 1e3, focal_length * 1e3, d_lens_root * 1e3, waist * 1e3, wavefront)
                    existing.add(key)
            except ValueError:
                csvu.append_result(roc * 1e3, focal_length * 1e3, "Error", "Error", "Error")


