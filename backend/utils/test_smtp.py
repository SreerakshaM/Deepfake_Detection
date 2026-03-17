import smtplib
from email.mime.text import MIMEText
import sys
import os

# Add backend to path to import Config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import Config

def test_smtp():
    print(f"Testing SMTP connection for: {Config.MAIL_USERNAME}")
    print(f"Using server: {Config.MAIL_SERVER}:{Config.MAIL_PORT}")
    
    msg = MIMEText("SMTP Test from Deepfake HUD")
    msg['Subject'] = "SMTP Connection Test"
    msg['From'] = Config.MAIL_USERNAME
    msg['To'] = Config.MAIL_USERNAME # Send to self

    try:
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(Config.MAIL_USERNAME, Config.MAIL_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("SUCCESS: SMTP connection established and test email sent.")
        return True
    except Exception as e:
        print(f"FAILURE: {e}")
        return False

if __name__ == "__main__":
    test_smtp()
