import cv2
import numpy as np
import os
import sys

def create_video(output_path, is_fake, duration_sec=5, fps=20, size=256):
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (size, size), isColor=False)
    total_frames = duration_sec * fps
    
    for i in range(total_frames):
        if is_fake:
            # Fake: Flatter spectrum with checkerboard artifacts
            f = np.fft.fftfreq(size)
            fx, fy = np.meshgrid(f, f)
            freq = np.sqrt(fx**2 + fy**2)
            freq[0, 0] = 1
            power = 1.0 / (freq ** 0.8)
            power[0, 0] = 0
            
            # Add strong checkerboard artifacts
            nyquist_mask = (np.abs(np.abs(fx) - 0.5) < 0.05) | (np.abs(np.abs(fy) - 0.5) < 0.05)
            power[nyquist_mask] *= 10.0
            
            phase = np.random.uniform(0, 2*np.pi, (size, size))
            spectrum = power * np.exp(1j * phase)
            img = np.real(np.fft.ifft2(spectrum))
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            cv2.putText(img, f"AI FAKE VIDEO - Frm {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,), 1)
        else:
            # Real: Natural 1/f noise spectrum
            f = np.fft.fftfreq(size)
            fx, fy = np.meshgrid(f, f)
            freq = np.sqrt(fx**2 + fy**2)
            freq[0, 0] = 1
            power = 1.0 / (freq ** 1.5)
            power[0, 0] = 0
            
            phase = np.random.uniform(0, 2*np.pi, (size, size))
            spectrum = power * np.exp(1j * phase)
            img = np.real(np.fft.ifft2(spectrum))
            img = cv2.normalize(img, None, 0, 255, cv2.NORM_MINMAX).astype(np.uint8)
            img = cv2.GaussianBlur(img, (3, 3), 0.5)
            noise = np.random.normal(0, 2, img.shape).astype(np.float32)
            img = np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
            cv2.putText(img, f"REAL VIDEO - Frm {i}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,), 1)
            
        out.write(img)
    out.release()
    print(f"Saved: {output_path}")

if __name__ == "__main__":
    out_dir = os.path.join(os.path.dirname(__file__), '..', 'sample_videos')
    os.makedirs(out_dir, exist_ok=True)
    
    create_video(os.path.join(out_dir, '1_real_camera.avi'), is_fake=False)
    create_video(os.path.join(out_dir, '2_ai_generated.avi'), is_fake=True)
