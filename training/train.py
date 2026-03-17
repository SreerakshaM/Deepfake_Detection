import numpy as np
import os
import cv2
import pickle
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import accuracy_score, classification_report
from frequency_transform import apply_fft

def load_data(data_dir):
    print("Loading datasets...")
    features = []
    labels = []
    
    for label_name, label_val in [('real', 0), ('fake', 1)]:
        folder = os.path.join(data_dir, label_name)
        if not os.path.exists(folder):
            print(f"Warning: Folder {folder} not found.")
            continue
        for filename in os.listdir(folder):
            img_path = os.path.join(folder, filename)
            features_1d = apply_fft(img_path)
            if features_1d is not None:
                features.append(features_1d)
                labels.append(label_val)
    
    return np.array(features), np.array(labels)

def train():
    base_dir = os.path.dirname(__file__)
    
    # Collect data from ALL available dataset folders:
    # 1. dataset/real + dataset/fake  (user-provided images)
    # 2. dataset/synthetic/real + dataset/synthetic/fake  (auto-generated)
    all_features = []
    all_labels = []
    
    data_sources = [
        os.path.join(base_dir, 'dataset'),           # user-provided
        os.path.join(base_dir, 'dataset/synthetic'),  # auto-generated
    ]
    
    for data_dir in data_sources:
        if os.path.exists(data_dir):
            X, y = load_data(data_dir)
            if len(X) > 0:
                all_features.extend(X)
                all_labels.extend(y)
                print(f"  Loaded {len(X)} samples from {data_dir}")
    
    if len(all_features) == 0:
        print("No training data found. Add images to training/dataset/real/ and training/dataset/fake/")
        return
    
    X = np.array(all_features)
    y = np.array(all_labels)
    print(f"\nTotal samples: {len(X)} ({sum(y==0)} real, {sum(y==1)} fake)")

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=300, random_state=42, n_jobs=-1)
    
    # Cross-validation for reliable accuracy estimate
    cv_scores = cross_val_score(model, X, y, cv=5, scoring='accuracy')
    print(f"Cross-validation accuracy: {cv_scores.mean()*100:.2f}% (+/- {cv_scores.std()*100:.2f}%)")
    
    model.fit(X_train, y_train)
    y_pred = model.predict(X_test)
    
    acc = accuracy_score(y_test, y_pred)
    print(f"Test accuracy: {acc*100:.2f}%")
    print(f"\nClassification Report:")
    print(classification_report(y_test, y_pred, target_names=['REAL', 'FAKE']))

    model_dir = os.path.join(os.path.dirname(__file__), '../backend/models')
    os.makedirs(model_dir, exist_ok=True)
    model_path = os.path.join(model_dir, 'deepfake_freq_model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    print(f"Model saved to {model_path}")

if __name__ == "__main__":
    train()
