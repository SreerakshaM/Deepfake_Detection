import os

class Config:
    UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), 'uploads')
    MODEL_PATH = os.path.join(os.path.dirname(__file__), 'models/deepfake_freq_model.pkl')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'mp4'}

    # Secret key for signing reset tokens
    SECRET_KEY = 'deepfake-forensic-hud-secret-key-2026'

    # SMTP Configuration for Gmail
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'sreeraksha452@gmail.com'  # Target sender
    MAIL_PASSWORD = 'hdex qtup ylrc fksr'