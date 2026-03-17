import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import Config

def send_reset_email(target_email, username, reset_link):
    """
    Sends a real password reset email using SMTP.
    The reset_link should already contain the secure token.
    """
    sender_email = Config.MAIL_USERNAME
    sender_password = Config.MAIL_PASSWORD
    
    if sender_password == 'your-app-password-here':
        print("ERROR: Email not sent. Please configure an App Password in config.py")
        return False, "SMTP configuration missing (App Password)."

    # Build the full URL
    full_reset_url = f"http://127.0.0.1:8000{reset_link}"

    # Create message
    msg = MIMEMultipart()
    msg['From'] = f"Deepfake Forensic Lab <{sender_email}>"
    msg['To'] = target_email
    msg['Subject'] = "SECURE ACCESS RECOVERY // Action Required"

    body = f"""
    SYSTEM NOTIFICATION: PASSWORD RESET REQUESTED
    ----------------------------------------------
    A request was made to reset the access key for user: {username}
    
    If this was you, please click the link below to reset your password:
    {full_reset_url}

    This link will expire in 1 hour for security purposes.

    SECURITY NOTICE: If you did not request this, please secure your account 
    immediately and ignore this message.

    -- FORENSIC HUD SYSTEM --
    """

    msg.attach(MIMEText(body, 'plain'))

    try:
        # Connect to Gmail SMTP server
        server = smtplib.SMTP(Config.MAIL_SERVER, Config.MAIL_PORT)
        server.starttls()
        server.login(sender_email, sender_password)
        
        # Send email
        server.send_message(msg)
        server.quit()
        print(f"Reset email sent to {target_email}")
        print(f"Reset link: {full_reset_url}")
        return True, "Email sent successfully."
    except Exception as e:
        print(f"SMTP Error: {e}")
        return False, str(e)
