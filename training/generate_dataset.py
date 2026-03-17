"""
Generates a realistic synthetic dataset for deepfake detection training.

REAL images: Simulated natural camera photos using:
  - Natural textures (1/f noise - power law decay with exponent ~1.2 to 1.8)
  - JPEG compression artifacts (save/reload at varying quality)
  - Gaussian sensor noise
  - Lens blur simulation
  - Natural texture patches and gradients

FAKE images: Simulated AI-generated images with artifacts from modern generators:
  - Smoother high-frequency decay (exponent ~0.5 to 1.0)
  - GAN upsampling artifacts (periodic peaks at various fractions of Nyquist)
  - Texture over-smoothing (high frequencies are suppressed)
  - Subtle grid artifacts from deconvolution / transposed convolution
  - Color/luminance distribution anomalies
  - Unnatural sharpness (no lens blur, reduced noise)
"""
import numpy as np
import cv2
import os


def generate_real_image(size=256):
    """Generate a realistic camera-like image using 1/f noise with camera pipeline."""
    # Vary the spectral exponent for diversity (natural images: 1.2 to 1.8)
    exponent = np.random.uniform(1.2, 1.8)

    f = np.fft.fftfreq(size)
    fx, fy = np.meshgrid(f, f)
    freq = np.sqrt(fx**2 + fy**2)
    freq[0, 0] = 1  # avoid division by zero

    # Natural 1/f^exponent power spectrum
    power = 1.0 / (freq ** exponent)
    power[0, 0] = 0

    # Random phase
    phase = np.random.uniform(0, 2 * np.pi, (size, size))
    spectrum = power * np.exp(1j * phase)

    img = np.real(np.fft.ifft2(spectrum))
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # Camera pipeline simulation:

    # 1. Lens blur (varies between cameras)
    blur_k = np.random.choice([3, 5, 7])
    sigma = np.random.uniform(0.3, 1.5)
    img = cv2.GaussianBlur(img, (blur_k, blur_k), sigma)

    # 2. Sensor noise (Gaussian + Poisson-like)
    noise_std = np.random.uniform(1.5, 5.0)
    noise = np.random.normal(0, noise_std, img.shape).astype(np.float32)
    img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    # 3. JPEG compression artifacts (cameras compress internally)
    quality = np.random.randint(70, 98)
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
    _, buf = cv2.imencode('.jpg', img, encode_param)
    img = cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE)

    # 4. Add occasional subtle gradients (from lighting)
    if np.random.random() < 0.5:
        gradient = np.linspace(0, np.random.uniform(5, 20), size).reshape(1, -1)
        if np.random.random() < 0.5:
            gradient = gradient.T
        img = np.clip(img.astype(np.float32) + gradient, 0, 255).astype(np.uint8)

    return img


def generate_fake_image(size=256):
    """Generate an AI-like image with frequency artifacts from modern generators."""
    # AI images have a shallower spectral decay (0.5 to 1.0 vs natural 1.2-1.8)
    exponent = np.random.uniform(0.5, 1.0)

    f = np.fft.fftfreq(size)
    fx, fy = np.meshgrid(f, f)
    freq = np.sqrt(fx**2 + fy**2)
    freq[0, 0] = 1

    power = 1.0 / (freq ** exponent)
    power[0, 0] = 0

    # --- Artifact 1: GAN upsampling peaks at Nyquist and sub-Nyquist ---
    # Peaks at f=0.5 (Nyquist from 2x upsampling)
    nyquist_strength = np.random.uniform(3.0, 10.0)
    nyquist_width = np.random.uniform(0.03, 0.07)
    nyquist_mask = (np.abs(np.abs(fx) - 0.5) < nyquist_width) | \
                   (np.abs(np.abs(fy) - 0.5) < nyquist_width)
    power[nyquist_mask] *= nyquist_strength

    # Peaks at f=0.25 (from 4x upsampling or 2-stage upsampling)
    if np.random.random() < 0.7:
        half_strength = np.random.uniform(1.5, 5.0)
        half_mask = (np.abs(np.abs(fx) - 0.25) < 0.03) | \
                    (np.abs(np.abs(fy) - 0.25) < 0.03)
        power[half_mask] *= half_strength

    # --- Artifact 2: Grid artifacts from transposed convolution ---
    if np.random.random() < 0.6:
        grid_freq = np.random.choice([0.125, 0.1667, 0.333])
        grid_strength = np.random.uniform(1.5, 4.0)
        grid_mask = (np.abs(np.abs(fx) - grid_freq) < 0.02) | \
                    (np.abs(np.abs(fy) - grid_freq) < 0.02)
        power[grid_mask] *= grid_strength

    # --- Artifact 3: Suppress high frequencies (over-smoothing) ---
    # AI images tend to have less natural high-frequency texture
    high_freq_mask = freq > np.random.uniform(0.3, 0.45)
    suppression = np.random.uniform(0.1, 0.5)
    power[high_freq_mask] *= suppression

    # Random phase
    phase = np.random.uniform(0, 2 * np.pi, (size, size))
    spectrum = power * np.exp(1j * phase)

    img = np.real(np.fft.ifft2(spectrum))
    img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)

    # AI images are often unnaturally sharp (no camera lens blur)
    # Only add very slight blur occasionally
    if np.random.random() < 0.2:
        img = cv2.GaussianBlur(img, (3, 3), 0.3)

    # Minimal noise (AI images have very low sensor noise)
    if np.random.random() < 0.3:
        noise = np.random.normal(0, 0.5, img.shape).astype(np.float32)
        img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)

    return img


def generate_dataset(output_dir, n_samples=500):
    """Generate the full dataset."""
    real_dir = os.path.join(output_dir, 'real')
    fake_dir = os.path.join(output_dir, 'fake')
    os.makedirs(real_dir, exist_ok=True)
    os.makedirs(fake_dir, exist_ok=True)

    print(f"Generating {n_samples} real images...")
    for i in range(n_samples):
        img = generate_real_image()
        cv2.imwrite(os.path.join(real_dir, f'real_{i}.jpg'), img)
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{n_samples} real images done")

    print(f"Generating {n_samples} fake images...")
    for i in range(n_samples):
        img = generate_fake_image()
        cv2.imwrite(os.path.join(fake_dir, f'fake_{i}.jpg'), img)
        if (i + 1) % 100 == 0:
            print(f"  {i+1}/{n_samples} fake images done")

    print(f"Done! Dataset saved to {output_dir}")


if __name__ == '__main__':
    output_dir = os.path.join(os.path.dirname(__file__), 'dataset/synthetic')
    generate_dataset(output_dir, n_samples=500)
