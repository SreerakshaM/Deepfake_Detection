import os
import sys
import numpy as np
import cv2
import pickle

# Add paths for imports
sys.path.append(os.path.join(os.getcwd(), 'backend'))
sys.path.append(os.path.join(os.getcwd(), 'training'))

from services.frequency_service import get_fft_spectrum
from generate_dataset import generate_real_image, generate_fake_image

def demo():
    model_path = 'backend/models/deepfake_freq_model.pkl'
    
    if not os.path.exists(model_path):
        print("Model not found. Please run training/train.py first.")
        return

    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    print("-" * 50)
    print("DEEPFAKE DETECTION DEMONSTRATION")
    print("-" * 50)

    # Create a temp directory for demo images
    temp_dir = 'training/demo_samples'
    os.makedirs(temp_dir, exist_ok=True)

    test_cases = [
        ("Real Image", generate_real_image, "demo_real.jpg"),
        ("AI Generated Image", generate_fake_image, "demo_fake.jpg")
    ]

    for label, generator, filename in test_cases:
        path = os.path.join(temp_dir, filename)
        img = generator()
        cv2.imwrite(path, img)

        # Process and predict
        spectrum = get_fft_spectrum(path)
        features = spectrum.reshape(1, -1)
        
        prob = model.predict_proba(features)[0][1]
        pred_label = "AI_GENERATED" if prob > 0.5 else "AUTHENTIC"
        
        print(f"\nTesting: {label}")
        print(f"File saved to: {path}")
        print(f"Prediction: {pred_label}")
        print(f"AI Probability: {prob:.4f}")
        
    print("-" * 50)

if __name__ == "__main__":
    demo()
