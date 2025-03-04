from flask_socketio import emit, join_room, leave_room, disconnect
from flask_jwt_extended import decode_token
from models import db, User
import jwt

def handle_socket_connections(socketio):

    def get_authenticated_user(sid):
        """Extract and verify JWT token from WebSocket connection."""
        token = None

        # Extract token from WebSocket `auth` object (sent by frontend)
        if sid in socketio.server.manager.get_participants("/", sid):
            auth_data = socketio.server.manager.get_participants("/", sid)[sid].get("auth", {})
            token = auth_data.get("token")

        if not token:
            emit("unauthorized", {"message": "Missing Authorization Header"})
            disconnect(sid)
            return None

        try:
            decoded = decode_token(token)
            user_id = decoded.get("sub")
            user = User.query.get(user_id)

            if not user:
                emit("unauthorized", {"message": "Invalid user"})
                disconnect(sid)
                return None

            return user

        except jwt.ExpiredSignatureError:
            emit("unauthorized", {"message": "Token expired"})
            disconnect(sid)
        except jwt.InvalidTokenError:
            emit("unauthorized", {"message": "Invalid token"})
            disconnect(sid)

        return None

    @socketio.on("connect")
    def on_connect():
        """Authenticate WebSocket connections using JWT."""
        user = get_authenticated_user(request.sid)
        if not user:
            return

        emit("authenticated", {"message": f"Welcome {user.username}"}, room=request.sid)

    @socketio.on("join")
    def handle_join(data):
        """Join a chat room securely."""
        user = get_authenticated_user(request.sid)
        if not user:
            return

        room = data.get("room")
        join_room(room)
        emit("message", {"user": "System", "message": f"{user.username} joined {room}"}, room=room)

    @socketio.on("leave")
    def handle_leave(data):
        """Leave a chat room."""
        user = get_authenticated_user(request.sid)
        if not user:
            return

        room = data.get("room")
        leave_room(room)
        emit("message", {"user": "System", "message": f"{user.username} left {room}"}, room=room)

    @socketio.on("message")
    def handle_message(data):
        """Send messages to a chat room securely."""
        user = get_authenticated_user(request.sid)
        if not user:
            return

        room = data.get("room")
        message = data.get("message")
        emit("message", {"user": user.username, "message": message}, room=room)