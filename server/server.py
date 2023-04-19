from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3 as sql

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

# create a database for a discord clone
with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (userId TEXT PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS binding (serverId TEXT, userId TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS servers (userId TEXT PRIMARY KEY, username TEXT, password TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS channels (channelId TEXT PRIMARY KEY, name TEXT, serverId TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS messages (messageId TEXT PRIMARY KEY, message TEXT, userId TEXT, channelId TEXT)")
    con.commit()

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
