import cv2
import numpy as np
import os
import sys

# Add training directory to path to reuse dataset generation logic
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'training'))
try:
    from generate_dataset import generate_real_image, generate_fake_image
except ImportError:
    # Fallback if imports fail
    def generate_real_image(size=256):
        return np.random.randint(0, 255, (size, size), dtype=np.uint8)
    def generate_fake_image(size=256):
        return np.random.randint(0, 255, (size, size), dtype=np.uint8)

def create_synthetic_video(output_path, duration_sec=5, fps=20, size=256):
    """
    Creates a video that alternates between 'Real' (natural noise) and 'Fake' (AI artifacts)
    to demonstrate diagnostic patterns.
    """
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(output_path, fourcc, fps, (size, size), isColor=False)
    
    total_frames = duration_sec * fps
    half_frames = total_frames // 2
    
    print(f"Generating {total_frames} frames for {output_path}...")
    
    # First half: Real images
    for i in range(half_frames):
        img = generate_real_image(size)
        # Add labels to the video frame
        cv2.putText(img, "REAL (Natural 1/f)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,), 1)
        out.write(img)
        
    # Second half: Fake images
    for i in range(half_frames, total_frames):
        img = generate_fake_image(size)
        cv2.putText(img, "FAKE (AI Artifacts)", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,), 1)
        out.write(img)
        
    out.release()
    print(f"Video saved to {output_path}")

if __name__ == "__main__":
    target_path = os.path.join(os.path.dirname(__file__), '..', 'sample_ai_video.avi')
    create_synthetic_video(target_path)
