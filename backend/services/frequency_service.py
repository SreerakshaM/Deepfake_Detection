import cv2
import numpy as np
import base64

def azimuthal_average(image, center=None):
    y, x = np.indices(image.shape)
    if not center:
        center = np.array([(y.max() - y.min()) / 2.0, (x.max() - x.min()) / 2.0])
    r = np.hypot(y - center[0], x - center[1]).astype(int)
    tbin = np.bincount(r.ravel(), image.ravel())
    nr = np.bincount(r.ravel())
    profile = tbin / nr
    # Normalize to focus on shape not absolute energy
    profile = profile / (np.mean(profile) + 1e-10)
    return profile

def get_fft_spectrum(image_path, size=(256, 256)):
    # Read image in grayscale
    img = cv2.imread(image_path, 0)
    if img is None:
        return None
    
    # Resize image
    img = cv2.resize(img, size)
    
    # Perform 2D FFT
    f = np.fft.fft2(img)
    fshift = np.fft.fftshift(f)
    magnitude_spectrum = np.abs(fshift)
    
    # Power spectrum for features
    psd = magnitude_spectrum ** 2
    psd_radial = azimuthal_average(psd)
    psd_radial = np.log(psd_radial + 1)
    
    return psd_radial
