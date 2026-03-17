import pickle
import os
import numpy as np
from config import Config

# Load the trained model
model = None
model_n_features = None
if os.path.exists(Config.MODEL_PATH):
    with open(Config.MODEL_PATH, 'rb') as f:
        model = pickle.load(f)
        model_n_features = model.n_features_in_
    print(f"[MODEL] Loaded model from {Config.MODEL_PATH} (expects {model_n_features} features)")
else:
    print(f"[MODEL] WARNING: Model not found at {Config.MODEL_PATH}! Predictions will return 0.5.")

def predict_deepfake(spectrum):
    if model is None:
        print("[PREDICT] No model loaded, returning 0.5")
        return 0.5
    
    # spectrum is a 1D radial profile from frequency_service
    features = spectrum.reshape(1, -1)
    
    # Handle feature length mismatch (image size can cause different radial profile lengths)
    feat_len = features.shape[1]
    if feat_len != model_n_features:
        print(f"[PREDICT] Feature length mismatch: got {feat_len}, expected {model_n_features}. Adjusting...")
        if feat_len > model_n_features:
            features = features[:, :model_n_features]
        else:
            features = np.pad(features, ((0, 0), (0, model_n_features - feat_len)))
    
    # Probability of class 1 (AI_GENERATED)
    try:
        prob = model.predict_proba(features)[0][1]
    except Exception as e:
        print(f"[PREDICT] predict_proba failed: {e}, falling back to predict")
        pred = model.predict(features)[0]
        prob = 0.9 if pred == 1 else 0.1
    
    print(f"[PREDICT] Prediction: {prob:.4f} ({'AI_GENERATED' if prob > 0.5 else 'AUTHENTIC'})")
    return float(prob)
