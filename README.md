# Deepfake Detection - Frequency Domain Analysis

This project implements a deepfake detection system that analyzes frequency-level artifacts using the Fast Fourier Transform (FFT).

## Project Overview
Generative models (GANs, Diffusion) often leave periodic artifacts in the frequency domain of the images they create. This tool converts images into their frequency spectrum and uses a Machine Learning model to detect these patterns.

## Features
- **Frequency Analysis**: Visualizes the 2D FFT magnitude spectrum.
- **ML Detection**: Uses a Random Forest Classifier (or CNN) to predict the probability of an image being a deepfake.
- **Forensic UI**: A modern dashboard designed for real-time analysis.

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Generate Synthetic Data** (for testing):
   ```bash
   python scripts/generate_synthetic_data.py
   ```

3. **Train the Model**:
   ```bash
   python scripts/train_model.py
   ```

4. **Run the Application**:
   - Start the backend:
     ```bash
     python app/backend/server.py
     ```
   - Open the frontend:
     Open `app/frontend/index.html` in your browser.

## Directory Structure
- `backend/`: Modular Flask setup.
  - `app.py`: Entry point.
  - `routes/detect_routes.py`: API endpoints.
  - `services/`: Logic for frequency analysis and prediction.
  - `utils/`: Preprocessing and file handling.
- `frontend/`: React components and static assets.
  - `public/`: Static HTML/CSS/JS assets.
- `training/`: Dedicated ML module for training and datasets.
  - `dataset/`: Training data.
  - `train.py`: Model training script.

