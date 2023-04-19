from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")


connected_users = set()


@socketio.on('connect')
def handle_connect():
    print('A user connected')
    emit('connectedUsers', list(connected_users), broadcast=True)


@socketio.on('disconnect')
def handle_disconnect():
    print('A user disconnected')
    emit('connectedUsers', list(connected_users), broadcast=True)


@socketio.on('message')
def handle_message(message):
    emit('message', message, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, port=3001)
