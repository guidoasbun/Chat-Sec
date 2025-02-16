from flask import Flask
from flask_socketio import SocketIO
import eventlet

# Import WebSocket handlers from separate file
from socket_handlers import register_socket_handlers

# Flask app setup
app = Flask(__name__)
app.config['SECRET_KEY'] = 'my_secret_key'

# WebSocket setup
socketio = SocketIO(app, cors_allowed_origins="*")

# Register WebSocket event handlers
register_socket_handlers(socketio)

@app.route('/')
def index():
    return "WebSocket Chat Server Running"

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
