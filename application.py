import os
from flask import Flask
from flask_migrate import Migrate
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Security configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET')

# Import models AFTER initializing Flask
from models import db, User, Session  # ✅ Import db from models AFTER app is initialized

# Initialize extensions
db.init_app(app)  # ✅ Register db with Flask here
migrate = Migrate(app, db)
jwt = JWTManager(app)
socketio = SocketIO(app, cors_allowed_origins="*")
CORS(app)

# Register blueprints
from auth_routes import auth_bp
app.register_blueprint(auth_bp, url_prefix="/api/auth")

from chat_routes import chat_bp, register_socketio_events
app.register_blueprint(chat_bp, url_prefix="/api/chat")

# Register WebSocket Handlers
register_socketio_events(socketio)

# Run the app
if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensures tables are created
    socketio.run(app, host="0.0.0.0", port=5005, debug=True)
