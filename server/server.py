from flask import Flask, redirect
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import sqlite3 as sql

app = Flask(__name__)
CORS(app, origins=["*"], supports_credentials=True)
socketio = SocketIO(app, cors_allowed_origins="*")

with sql.connect("database.db") as con:
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, avatar TEXT, discriminator TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS servers (id INTEGER PRIMARY KEY, name TEXT, owner_id INTEGER, icon TEXT)")
    cur.execute("CREATE TABLE IF NOT EXISTS server_members (server_id INTEGER, user_id INTEGER, FOREIGN KEY(server_id) REFERENCES servers(id), FOREIGN KEY(user_id) REFERENCES users(id))")
    cur.execute("CREATE TABLE IF NOT EXISTS channels (id INTEGER PRIMARY KEY, name TEXT, type TEXT, server_id INTEGER, FOREIGN KEY(server_id) REFERENCES servers(id))")
    cur.execute("CREATE TABLE IF NOT EXISTS channel_members (channel_id INTEGER, user_id INTEGER, FOREIGN KEY(channel_id) REFERENCES channels(id), FOREIGN KEY(user_id) REFERENCES users(id))")
    cur.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY, content TEXT, author_id INTEGER, channel_id INTEGER, timestamp TEXT, FOREIGN KEY(author_id) REFERENCES users(id), FOREIGN KEY(channel_id) REFERENCES channels(id))")
    con.commit()

connected_users = set()

@app.route('/')
def redir():
    return redirect('http://localhost:5173/')

@socketio.on('connect')
def handle_connect():
    print('Connected Client')
    emit('connectedUsers', list(connected_users), broadcast=True)

@socketio.on('disconnect')
def handle_disconnect():
    print('Disconnected Client')
    emit('connectedUsers', list(connected_users), broadcast=True)

@socketio.on('login')
def handle_login(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ? AND password = ?", (data['username'], data['password']))
        user = cur.fetchone()
        if user:
            connected_users.add(user[0])
            user_data = {
                "id": user[0],
                "username": user[1],
                "avatar": user[3],
                "discriminator": user[4],
                "public_flags": 0
            }
            emit('login', {'token': "dummy_token", 'user': user_data})
        else:
            emit('login', {'error': "Invalid username or password"})

@socketio.on('register')
def handle_register(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT * FROM users WHERE username = ?", (data['username'],))
        user = cur.fetchone()
        if user:
            emit('register', {'success': False})
        else:
            cur.execute("INSERT INTO users (username, password) VALUES (?, ?)", (data['username'], data['password']))
            con.commit()
            emit('register', {'success': True})

@socketio.on('getConnectedUsers')
def handle_get_connected_users():
    emit('connectedUsers', list(connected_users))

@socketio.on('getConnectedServers')
def handle_get_connected_servers(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT s.id, s.name, s.icon FROM servers s JOIN server_members sm ON s.id = sm.server_id WHERE sm.user_id = ?", (data['userId'],))
        servers = cur.fetchall()
        server_data = []
        for server in servers:
            server_data.append({
                "id": server[0],
                "name": server[1],
                "icon": server[2],
                "owner_id": server[3]
            })
        emit('getConnectedServers', {'servers': server_data})

@socketio.on('getChannels')
def handle_get_channels(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id, name, type FROM channels WHERE server_id = ?", (data['serverId'],))
        channels = cur.fetchall()
        channel_data = []
        for channel in channels:
            channel_data.append({
                "id": channel[0],
                "name": channel[1],
                "type": channel[2]
            })
        emit('getChannels', {'channels': channel_data})

@socketio.on('getMessages')
def handle_get_messages(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("SELECT id, content, author_id, timestamp FROM messages WHERE channel_id = ?", (data['channelId'],))
        messages = cur.fetchall()
        message_data = []
        for message in messages:
            message_data.append({
                "id": message[0],
                "content": message[1],
                "author_id": message[2],
                "timestamp": message[3]
            })
        emit('getMessages', {'messages': message_data})

@socketio.on('sendMessage')
def handle_send_message(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO messages (content, author_id, channel_id, timestamp) VALUES (?, ?, ?, datetime('now'))", (data['content'], data['author_id'], data['channel_id']))
        con.commit()
        emit('sendMessage', {
            "id": cur.lastrowid,
            "content": data['content'],
            "author_id": data['author_id'],
            "channel_id": data['channel_id'],
            "timestamp": "now"
        }, broadcast=True)

@socketio.on('createServer')
def handle_create_server(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO servers (name, owner_id, icon) VALUES (?, ?, ?)", (data['name'], data['owner_id'], data['icon']))
        con.commit()
        server_id = cur.lastrowid
        cur.execute("INSERT INTO server_members (server_id, user_id) VALUES (?, ?)", (server_id, data['owner_id']))
        con.commit()
        emit('createServer', {
            "id": server_id,
            "name": data['name'],
            "owner_id": data['owner_id'],
            "icon": data['icon']
        }, broadcast=True)

@socketio.on('createChannel')
def handle_create_channel(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO channels (name, type, server_id) VALUES (?, ?, ?)", (data['name'], data['type'], data['server_id']))
        con.commit()
        channel_id = cur.lastrowid
        emit('createChannel', {
            "id": channel_id,
            "name": data['name'],
            "type": data['type'],
            "server_id": data['server_id']
        }, broadcast=True)

@socketio.on('joinServer')
def handle_join_server(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("INSERT INTO server_members (server_id, user_id) VALUES (?, ?)", (data['server_id'], data['user_id']))
        con.commit()
        emit('joinServer', {
            "server_id": data['server_id'],
            "user_id": data['user_id']
        }, broadcast=True)

@socketio.on('leaveServer')
def handle_leave_server(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM server_members WHERE server_id = ? AND user_id = ?", (data['server_id'], data['user_id']))
        con.commit()
        emit('leaveServer', {
            "server_id": data['server_id'],
            "user_id": data['user_id']
        }, broadcast=True)

@socketio.on('deleteServer')
def handle_delete_server(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM servers WHERE id = ?", (data['server_id'],))
        con.commit()
        emit('deleteServer', {
            "server_id": data['server_id']
        }, broadcast=True)

@socketio.on('deleteChannel')
def handle_delete_channel(data):
    with sql.connect("database.db") as con:
        cur = con.cursor()
        cur.execute("DELETE FROM channels WHERE id = ?", (data['channel_id'],))
        con.commit()
        emit('deleteChannel', {
            "channel_id": data['channel_id']
        }, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, port=3001)