from flask import request
from flask_socketio import emit

# Store connected users (optional tracking)
connected_users = {}

def register_socket_handlers(socketio):
    @socketio.on('connect')
    def handle_connect():
        print(f"User connected: {request.sid}")
        connected_users[request.sid] = True
        emit('server_message', {'message': 'Connected to server'})

    @socketio.on('disconnect')
    def handle_disconnect():
        print(f"User disconnected: {request.sid}")
        connected_users.pop(request.sid, None)

    @socketio.on('send_message')
    def handle_message(data):
        message = data.get('message')
        if message:
            print(f"Received message: {message}")
            emit('receive_message', {'message': message}, broadcast=True)
