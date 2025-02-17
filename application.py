from flask import Flask
from flask_socketio import SocketIO

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secret_key"

socketio = SocketIO(app, cors_allowed_origins="*")

@socketio.on("connect")
def handle_connect():
    print("Client connected")
    socketio.emit("server_message", {"message": "Connected to WebSocket!"})

@socketio.on("send_message")
def handle_message(data):
    message = data.get("message")
    if message:
        socketio.emit("receive_message", {"message": message}, broadcast=True)

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000)
