from flask import Flask
from flask_cors import CORS
from itsdangerous import URLSafeTimedSerializer
from config import Config
from routes.detect_routes import detect_bp
from routes.auth_routes import auth_bp

app = Flask(__name__, static_folder='../frontend/public', static_url_path='')
CORS(app)

# Initialize the token serializer for secure reset links
serializer = URLSafeTimedSerializer(Config.SECRET_KEY)

# Store serializer in app config so routes can access it
app.config['SERIALIZER'] = serializer

# Register blueprints
app.register_blueprint(detect_bp)
app.register_blueprint(auth_bp)

@app.route('/')
def index():
    return app.send_static_file('index.html')

if __name__ == '__main__':
    app.run(debug=True, port=8000)
