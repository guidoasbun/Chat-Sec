# Modified chat_routes.py - Remove @jwt_required from socket handlers

from flask_socketio import emit, join_room, leave_room
from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity, decode_token
from models import db, User
import jwt

chat_bp = Blueprint("chat", __name__)

# Store active rooms (for demo purposes)
active_rooms = {}


@chat_bp.route("/message", methods=["POST"])
@jwt_required()
def send_message():
    """API route for sending messages"""
    from application import socketio  # Delayed import to avoid circular import issue

    user_id = get_jwt_identity()
    data = request.json

    message = data.get("message")
    room = data.get("room")

    if not message or not room:
        return jsonify({"error": "Message and room are required"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    # Emit message via WebSocket
    socketio.emit("message", {"user": user.username, "message": message}, room=room)

    return jsonify({"message": "Message sent", "room": room, "user": user.username}), 200


# WebSocket event handlers
def register_socketio_events(socketio):
    """Register WebSocket events after socketio is initialized"""

    def get_user_from_token(auth_data):
        """Extract user from token in socket auth data"""
        if not auth_data or 'token' not in auth_data:
            return None

        token = auth_data.get('token')
        try:
            # Get the JWT secret key from app config
            from flask import current_app
            jwt_secret = current_app.config['JWT_SECRET_KEY']

            # Decode token manually
            decoded = jwt.decode(
                token,
                jwt_secret,
                algorithms=['HS256']
            )

            # Get user from decoded token
            user_id = decoded.get('sub')  # flask-jwt-extended uses 'sub' for the identity
            user = User.query.get(user_id)
            return user
        except Exception as e:
            print(f"Token authentication error: {str(e)}")
            return None

    @socketio.on("connect")
    def handle_connect():
        """Authenticate user on connection"""
        auth = request.args.get('auth') or {}
        # Flask-SocketIO puts auth data in different places depending on how it was sent
        if hasattr(request, 'headers') and request.headers.get('Authorization'):
            token = request.headers.get('Authorization')
            if token.startswith('Bearer '):
                token = token[7:]
            auth = {'token': token}
        elif hasattr(request, '_auth') and request._auth:
            auth = request._auth

        user = get_user_from_token(auth)
        if not user:
            # We'll allow the connection but track as unauthenticated
            # This allows us to send an error message before disconnecting
            emit("unauthorized", {"message": "Authentication required"})
            return False

        # Store user info in the request for later use
        request.user = user
        emit("authenticated", {"user": user.username})
        return True

    @socketio.on("join")
    def handle_join(data):
        """Join a chat room securely."""
        user = getattr(request, 'user', None)
        if not user:
            emit("unauthorized", {"message": "Authentication required"})
            return

        room = data.get("room")
        join_room(room)
        active_rooms[user.username] = room
        emit("message", {"user": "System", "message": f"{user.username} joined {room}"}, room=room)

    @socketio.on("leave")
    def handle_leave(data):
        """Leave a chat room."""
        user = getattr(request, 'user', None)
        if not user:
            emit("unauthorized", {"message": "Authentication required"})
            return

        room = data.get("room")
        leave_room(room)
        active_rooms.pop(user.username, None)
        emit("message", {"user": "System", "message": f"{user.username} left {room}"}, room=room)

    @socketio.on("message")
    def handle_message(data):
        """Send messages to a chat room securely."""
        user = getattr(request, 'user', None)
        if not user:
            emit("unauthorized", {"message": "Authentication required"})
            return

        message = data.get("message")
        room = data.get("room")

        emit("message", {"user": user.username, "message": message}, room=room)