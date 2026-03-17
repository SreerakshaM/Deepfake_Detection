import cv2
import numpy as np

def azimuthal_average(image, center=None):
    """
    Calculate the azimuthally averaged radial profile.
    """
    y, x = np.indices(image.shape)
    if not center:
        center = np.array([(y.max() - y.min()) / 2.0, (x.max() - x.min()) / 2.0])

    r = np.hypot(y - center[0], x - center[1])
    r = r.astype(int)

    tbin = np.bincount(r.ravel(), image.ravel())
    nr = np.bincount(r.ravel())
    radialprofile = tbin / nr
    # Normalize to focus on shape not absolute energy
    radialprofile = radialprofile / (np.mean(radialprofile) + 1e-10)
    return radialprofile

def apply_fft(image_path, size=(256, 256)):
    img = cv2.imread(image_path, 0)
    if img is None:
        return None
    img = cv2.resize(img, size)
    
    # FFT
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = np.abs(fshift)
    
    # Power spectrum
    psd = magnitude_spectrum ** 2
    
    # Radial profile (Azimuthal Average)
    psd_radial = azimuthal_average(psd)
    
    # Logistics for numerical stability
    psd_radial = np.log(psd_radial + 1)
    
    return psd_radial
