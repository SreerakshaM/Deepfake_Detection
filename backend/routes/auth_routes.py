import os
import json
from flask import Blueprint, request, jsonify, current_app
from utils.email_service import send_reset_email

auth_bp = Blueprint('auth', __name__)

# Mock user database
USERS_FILE = os.path.join(os.path.dirname(__file__), '..', 'users.json')

def load_users():
    if not os.path.exists(USERS_FILE):
        initial_users = {
            "admin": "password123",
            "testuser": {
                "password": "password456",
                "email": "test@gmail.com",
                "phone": "1234567890"
            },
            "sreeraksha": {
                "password": "Amulya@20",
                "email": "sreeraksha452@gmail.com",
                "phone": "9876543210"
            }
        }
        save_users(initial_users)
        return initial_users
    
    with open(USERS_FILE, 'r') as f:
        return json.load(f)

def save_users(users_dict):
    with open(USERS_FILE, 'w') as f:
        json.dump(users_dict, f, indent=4)

# Global users dictionary (will be synced with file)
users = load_users()

@auth_bp.route('/api/login', methods=['POST'])
def login():
    global users
    users = load_users() # Refresh from disk in case of external changes
    data = request.json
    email = data.get('email')
    password = data.get('password')

    # Search for user by email
    matched_username = None
    matched_user = None
    for uname, user_data in users.items():
        if isinstance(user_data, dict) and user_data.get('email') == email:
            matched_username = uname
            matched_user = user_data
            break

    if matched_user and matched_user.get('password') == password:
        return jsonify({'message': 'Login successful', 'user': matched_username}), 200
    else:
        return jsonify({'message': 'Invalid credentials. Check your Gmail and password.'}), 401

@auth_bp.route('/api/signup', methods=['POST'])
def signup():
    global users
    users = load_users()
    data = request.json
    username = data.get('username')
    email = data.get('email')
    phone = data.get('phone')
    password = data.get('password')
    
    if username in users:
        return jsonify({'message': 'User already exists'}), 400
    
    users[username] = {
        'password': password,
        'email': email,
        'phone': phone
    }
    save_users(users)
    return jsonify({'message': 'User created successfully'}), 201

@auth_bp.route('/api/reset-password', methods=['POST'])
def reset_password():
    data = request.json
    token = data.get('token')
    new_password = data.get('password')
    
    if not token or not new_password:
        return jsonify({'message': 'Token and password are required'}), 400

    # Validate the token
    serializer = current_app.config['SERIALIZER']
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except Exception:
        return jsonify({'message': 'Invalid or expired reset link. Please request a new one.'}), 400

    # Find user by email and update password
    global users
    users = load_users()
    for username, user_data in users.items():
        if isinstance(user_data, dict) and user_data.get('email') == email:
            users[username]['password'] = new_password
            save_users(users)
            return jsonify({'message': 'Password reset successfully'}), 200

    return jsonify({'message': 'User not found'}), 404

@auth_bp.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    data = request.json
    email = data.get('email')
    
    # Search for user with this email
    target_username = None
    for username, user_data in users.items():
        if isinstance(user_data, dict) and user_data.get('email') == email:
            target_username = username
            break
    
    if target_username:
        # Generate a secure time-limited token
        serializer = current_app.config['SERIALIZER']
        token = serializer.dumps(email, salt='password-reset')
        
        reset_link = f'/reset_password.html?token={token}'
        success, message = send_reset_email(email, target_username, reset_link)
        
        if success:
            return jsonify({
                'message': f'A recovery email has been sent to {email}. Please check your inbox.',
                'status': 'sent'
            }), 200
        else:
            return jsonify({
                'message': f'Error sending email: {message}',
                'status': 'error'
            }), 500
    else:
        return jsonify({'message': 'No account associated with this Gmail ID.'}), 404

@auth_bp.route('/api/verify-reset-token', methods=['POST'])
def verify_reset_token():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({'message': 'No token provided'}), 400

    serializer = current_app.config['SERIALIZER']
    try:
        email = serializer.loads(token, salt='password-reset', max_age=3600)
    except Exception:
        return jsonify({'message': 'Invalid or expired reset link. Please request a new one.'}), 400

    # Find the username for this email
    for username, user_data in users.items():
        if isinstance(user_data, dict) and user_data.get('email') == email:
            return jsonify({'message': 'Token is valid', 'username': username, 'email': email}), 200

    return jsonify({'message': 'User not found'}), 404
