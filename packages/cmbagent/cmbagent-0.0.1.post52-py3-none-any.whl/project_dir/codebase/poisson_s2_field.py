# filename: codebase/poisson_s2_field.py
import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import os
import time

def generate_poisson_points_on_s2(lambda_sphere):
    """
    Generate a Poisson point process on the unit sphere S^2.
    Parameters
    ----------
    lambda_sphere : float
        Mean number of points (intensity) on the sphere.
    Returns
    -------
    points : ndarray, shape (N, 3)
        Cartesian coordinates of the points on S^2.
    """
    N = np.random.poisson(lambda_sphere)
    # Uniformly sample points on S^2
    phi = np.random.uniform(0, 2*np.pi, N)  # azimuthal angle [rad]
    cos_theta = np.random.uniform(-1, 1, N)   # cos(polar angle)
    theta = np.arccos(cos_theta)              # polar angle [rad]
    x = np.sin(theta) * np.cos(phi)
    y = np.sin(theta) * np.sin(phi)
    z = np.cos(theta)
    points = np.stack((x, y, z), axis=1)
    return points, theta, phi

def gaussian_kernel_on_sphere(ang_dist, sigma_rad):
    """
    Gaussian kernel on the sphere as a function of angular distance.
    Parameters
    ----------
    ang_dist : ndarray
        Angular distance(s) [rad].
    sigma_rad : float
        Gaussian width [rad].
    Returns
    -------
    kernel : ndarray
        Kernel value(s).
    """
    return np.exp(-0.5 * (ang_dist / sigma_rad)**2)

def compute_scalar_field_on_healpix(points, nside, sigma_deg):
    """
    Compute the scalar field on a HEALPix grid by smoothing Poisson points with a Gaussian kernel.
    Parameters
    ----------
    points : ndarray, shape (N, 3)
        Cartesian coordinates of the points on S^2.
    nside : int
        HEALPix nside parameter.
    sigma_deg : float
        Gaussian kernel width [deg].
    Returns
    -------
    field : ndarray, shape (npix,)
        Scalar field on the HEALPix grid.
    """
    npix = hp.nside2npix(nside)
    # Get pixel centers in (theta, phi)
    theta_pix, phi_pix = hp.pix2ang(nside, np.arange(npix))
    # Convert sigma to radians
    sigma_rad = np.deg2rad(sigma_deg)
    field = np.zeros(npix)
    # For each point, add a Gaussian bump to the field
    for i in range(points.shape[0]):
        # Point direction
        vec = points[i]
        # Compute angular distance to all pixels
        pix_vecs = hp.ang2vec(theta_pix, phi_pix)
        ang_dist = np.arccos(np.clip(np.dot(pix_vecs, vec), -1, 1))  # [rad]
        field += gaussian_kernel_on_sphere(ang_dist, sigma_rad)
    return field

def plot_field_and_power_spectrum(field, nside, plot_prefix, plot_number, timestamp, database_path):
    """
    Plot the scalar field on the sphere and its angular power spectrum.
    Parameters
    ----------
    field : ndarray
        Scalar field on the HEALPix grid.
    nside : int
        HEALPix nside parameter.
    plot_prefix : str
        Prefix for plot filenames.
    plot_number : int
        Plot number for filename.
    timestamp : str
        Timestamp string for filename.
    database_path : str
        Directory to save plots.
    """
    if not os.path.exists(database_path):
        os.makedirs(database_path)
    # Plot field (Mollweide projection)
    plt.figure(figsize=(10, 6))
    hp.mollview(field, title="Gaussian-smoothed Poisson Field on S2", unit="arbitrary", cmap="viridis", cbar=True, notext=True)
    plt.tight_layout()
    field_plot_filename = database_path + plot_prefix + "_field_" + str(plot_number) + "_" + timestamp + ".png"
    plt.savefig(field_plot_filename, dpi=300)
    plt.close()
    print("Saved Mollweide projection of the scalar field to " + field_plot_filename)
    # Compute and plot angular power spectrum
    cl = hp.anafast(field)
    ell = np.arange(len(cl))
    plt.figure(figsize=(8, 5))
    plt.plot(ell, cl, lw=2)
    plt.xlabel("Multipole moment l")
    plt.ylabel("C_l (arbitrary units)")
    plt.title("Angular Power Spectrum of the Field")
    plt.grid(True, which="both", ls="--", alpha=0.5)
    plt.tight_layout()
    ps_plot_filename = database_path + plot_prefix + "_powerspectrum_" + str(plot_number) + "_" + timestamp + ".png"
    plt.savefig(ps_plot_filename, dpi=300)
    plt.close()
    print("Saved angular power spectrum plot to " + ps_plot_filename)
    # Print some details
    print("Field mean: " + str(np.mean(field)))
    print("Field std: " + str(np.std(field)))
    print("First 10 C_l values: " + str(cl[:10]))

def main():
    """
    Main routine to generate a Poisson point process on S^2, compute the scalar field,
    and plot the field and its angular power spectrum.
    """
    # Parameters
    lambda_sphere = 500      # mean number of points on S^2 [dimensionless]
    nside = 64               # HEALPix nside (resolution parameter)
    sigma_deg = 3.0          # Gaussian kernel width [deg]
    database_path = "data/"
    plot_prefix = "poisson_s2"
    plot_number = 1
    timestamp = str(int(time.time()))
    # Generate Poisson points
    points, theta, phi = generate_poisson_points_on_s2(lambda_sphere)
    print("Generated " + str(points.shape[0]) + " Poisson points on S^2.")
    # Compute scalar field
    field = compute_scalar_field_on_healpix(points, nside, sigma_deg)
    # Plot field and power spectrum
    plot_field_and_power_spectrum(field, nside, plot_prefix, plot_number, timestamp, database_path)

if __name__ == "__main__":
    main()
