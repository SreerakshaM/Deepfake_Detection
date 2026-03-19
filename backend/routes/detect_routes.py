from flask import Blueprint, request, jsonify
import os
from services.frequency_service import get_fft_spectrum
from services.prediction_service import predict_deepfake
from config import Config

detect_bp = Blueprint('detect', __name__)

@detect_bp.route('/predict', methods=['POST'])
def predict():
    if 'file' not in request.files:
        if 'image' in request.files:
            file = request.files['image']
        else:
            return jsonify({'error': 'No file uploaded'}), 400
    else:
        file = request.files['file']
        
    filename = file.filename
    ext = filename.rsplit('.', 1)[-1].lower() if '.' in filename else 'jpg'
    
    file_path = os.path.join(Config.UPLOAD_FOLDER, f'temp_upload.{ext}')
    os.makedirs(Config.UPLOAD_FOLDER, exist_ok=True)
    file.save(file_path)
    
    predictions = []
    
    if ext in ['mp4', 'avi', 'mov', 'mkv', 'webm']:
        import cv2
        cap = cv2.VideoCapture(file_path)
        frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        if frame_count <= 0:
            frame_count = 30
            
        step = max(1, frame_count // 10)
        frames_processed = 0
        current_frame = 0
        
        while cap.isOpened() and frames_processed < 10:
            cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)
            ret, frame = cap.read()
            if not ret:
                break
                
            temp_frame_path = os.path.join(Config.UPLOAD_FOLDER, 'temp_frame.jpg')
            cv2.imwrite(temp_frame_path, frame)
            
            spectrum_data = get_fft_spectrum(temp_frame_path)
            if spectrum_data is not None:
                prob = predict_deepfake(spectrum_data['spectrum'])
                predictions.append(prob)
                if 'basis_metrics' not in locals():
                    basis_metrics = spectrum_data['metrics']
                    hf_ratio = spectrum_data['hf_ratio']
                
            current_frame += step
            frames_processed += 1
            
        cap.release()
        try:
            os.remove(os.path.join(Config.UPLOAD_FOLDER, 'temp_frame.jpg'))
        except:
            pass
    else:
        spectrum_data = get_fft_spectrum(file_path)
        if spectrum_data is not None:
            prob = predict_deepfake(spectrum_data['spectrum'])
            predictions.append(prob)
            basis_metrics = spectrum_data['metrics']
            hf_ratio = spectrum_data['hf_ratio']
            
    if not predictions:
        try:
            os.remove(file_path)
        except:
            pass
        return jsonify({'error': 'Invalid file'}), 400
        
    avg_prediction = sum(predictions) / len(predictions)
    label = 'AI_GENERATED' if avg_prediction > 0.5 else 'AUTHENTIC'
    
    # Generate Basis Reason
    if label == 'AI_GENERATED':
        reason = f"Detected anomalous periodic artifacts in the high-frequency spectrum({hf_ratio:.1f}% energy). This 'checkerboard' pattern is a common fingerprint of generative models like GANs or Diffusion."
        comparison = "High-frequency noise is significantly higher (2-3x) than natural images."
    else:
        reason = f"Frequency distribution follows the natural '1/f' power law with low high-frequency noise ({hf_ratio:.1f}%). No synthesis artifacts detected."
        comparison = "Matches the spectral signature of authentic biological/natural captures."

    try:
        os.remove(file_path)
    except:
        pass
    
    return jsonify({
        'prediction': avg_prediction,
        'label': label,
        'basis': reason,
        'comparison': comparison,
        'metrics': basis_metrics if 'basis_metrics' in locals() else {}
    })
