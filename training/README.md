# Deepfake Model Training Guide

This directory contains scripts and data needed to train the frequency-domain deepfake detection model used in the backend.

## Model Overview
The model uses **Fast Fourier Transform (FFT)** to analyze the frequency signature of images. AI-generated images often leave "checkerboard" artifacts in the frequency domain that are invisible to the human eye but easily detectable by this model.

## Folder Structure
- `dataset/`: 
  - `real/`: Place authentic images here.
  - `fake/`: Place AI-generated/Deepfake images here.
- `synthetic/`: Contains auto-generated samples for demonstration.
- `train.py`: The main training script.
- `generate_dataset.py`: A script to generate synthetic training data if you don't have enough real samples.
- `frequency_transform.py`: Core utility for extracting FFT features.

## How to Train

### 1. Prepare your Dataset
Place as many `real` and `fake` images as possible in the `dataset/` subfolders.
- Aim for at least 100 images in each category for decent results.
- Images should ideally be faces, as deepfakes are most common in facial videos.

### 2. (Optional) Generate Synthetic Data
If you don't have enough images, you can generate a synthetic dataset:
```bash
python training/generate_dataset.py
```
This will create 200 real-like and 200 fake-like images in `training/dataset/synthetic/`.

### 3. Run the Training
Execute the training script:
```bash
python training/train.py
```
This script will:
1. Load all images from `dataset/real`, `dataset/fake`, and `dataset/synthetic`.
2. Extract frequency features.
3. Train a Random Forest classifier.
4. Save the trained model to `backend/models/deepfake_freq_model.pkl`.

## Video Detection Workflow
When a video is uploaded to the backend:
1. The backend extracts 10 frames from across the video's duration.
2. Each frame is analyzed by the trained FFT model.
3. The results are averaged:
   - If Average > 0.5: Classified as **AI_GENERATED**.
   - If Average <= 0.5: Classified as **AUTHENTIC**.

## Troubleshooting
- **Missing Dependencies**: Ensure you have run `pip install -r requirements.txt`.
- **Low Accuracy**: Increase the number of real/fake samples in your dataset.
- **Model not updating**: Ensure the `backend/models` directory is writable.
