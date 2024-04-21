# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

rooms = {}
users = {} # maps sid to username
sidToUsername = {}
userrooms = {}
roomToHost = {} # maps room to sid of the host
connections = []


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/<room>')
def room(room):
    return render_template('index.html', room=room)

@socketio.on("new user")
def handle_new_user(username):
    print(f"new user {username} is here")
    users[request.sid] = username
    connections.append(request.sid)
    sidToUsername[request.sid] = username
    emit('user added', {'success': True})

def updateRoomUsers(roomnum):
    room_name = "room-" + roomnum
    room = rooms.get(room_name)
    print(room)
    if room is not None:
        print("uru if true")
        roomUsers = room.get('users', [])
        print(roomUsers)
        # socketio.emit('get users', roomUsers)
        socketio.emit('get users', roomUsers, room=room_name)

def updateQueueVideos(roomnum):
    room_name = "room-" + roomnum
    room = rooms.get(room_name)
    if room is not None:
        print("uqv if true")
        vidlist = room.get('queue', {})
        currPlayer = room.get('currPlayer', 0)
        # socketio.emit('get vidlist', {'vidlist': vidlist, 'currPlayer': currPlayer})
        socketio.emit('get vidlist', {'vidlist': vidlist, 'currPlayer': currPlayer}, room=room_name)

@socketio.on("new room")
def handle_new_room(roomnum):
    room_name = "room-" + str(roomnum)

    userrooms[request.sid] = roomnum

    host = None
    init = False

    if roomnum is None or roomnum == "":
        roomnum = '1'
        userrooms[request.sid] = '1'

    join_room(room_name)

    if room_name not in rooms:
        rooms[room_name] = {
            'host': None,
            'currPlayer': 0,
            'currVideo': {'yt': 'tXha7F48HyU'},
            'prevVideo': {'yt': {'id': 'tXha7F48HyU', 'time': 0}},
            'hostName': None,
            'users': [],
            'queue': {'yt': []}
        }

    print(roomnum, type(roomnum))

    if rooms[room_name]['host'] is None:
        rooms[room_name]['host'] = request.sid
        host = request.sid
        init = True
        print("ready to emit setHost")
        emit('setHost', {'success': True})

    else:
        host = rooms[room_name]['host']

    if init:
        rooms[room_name]['hostName'] = sidToUsername[request.sid]
        rooms[room_name]['users'].append(sidToUsername[request.sid])

    emit('changeHostLabel', {'username': rooms[room_name]['hostName']}, room=room_name)


    print("hello")
    updateQueueVideos(roomnum)

    currVideo = rooms[room_name]['currVideo']['yt']

    emit('changeVideoClient', {'videoId': currVideo}, room=room_name)

    if request.sid != host:
        socketio.sleep(1)
        # emit('getData', room=host)
        emit('syncHost', room=roomnum, broadcast=True)
        rooms[room_name]['users'].append(sidToUsername[request.sid])

    updateRoomUsers(roomnum)
    # return True

@socketio.on('play video')
def handle_play_video(data):
    roomnum = data['room']
    print("hello pvc")
    socketio.emit('playVideoClient', room="room-" + roomnum)
    # socketio.emit('playVideoClient', {"success":True}) #this line change 

@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    username = users.get(user_id)
    if username:
        del users[user_id]
    
    if user_id in connections:
        connections.remove(user_id)

    room_num = userrooms.get(user_id)
    room_name = "room-" + str(room_num)
    room = rooms.get(room_name)

    if room:
        if user_id == room.get('host'):
            first_user_id = list(room.get('sockets'))[0]
            socketio.emit('autoHost', {'roomnum': room_num}, room=first_user_id)

        if username in room.get('users', []):
            room['users'].remove(username)
            updateRoomUsers(room_num)

    del userrooms[user_id]


@socketio.on('sync video')
def handle_sync_video(data):
    room_num = data.get('room')
    time = data.get('time')
    state = data.get('state')
    video_id = data.get('videoId')
    player_id = rooms.get("room-" + str(room_num), {}).get('currPlayer')
    socketio.emit('syncVideoClient', {'time': time, 'state': state, 'videoId': video_id, 'playerId': player_id}, room="room-" + str(room_num))

@socketio.on('play other')
def handle_play_other(data):
    room_num = data.get('room')
    socketio.emit('justPlay', room="room-" + str(room_num), skip_sid=request.sid)

@socketio.on('pause other')
def handle_pause_other(data):
    room_num = data.get('room')
    socketio.emit('justPause', room="room-" + str(room_num), skip_sid=request.sid)

@socketio.on('seek other')
def handle_seek_other(data):
    room_num = data.get('room')
    curr_time = data.get('time')
    socketio.emit('justSeek', {'time': curr_time}, room="room-" + str(room_num), skip_sid=request.sid)

@socketio.on('get video')
def handle_get_video():
    print("inside handle get video")
    room_num = userrooms.get(request.sid)
    if room_num:
        curr_video = rooms.get("room-" + str(room_num), {}).get('currVideo', {}).get('yt')
        socketio.emit('get video callback', curr_video, room="room-" + str(room_num))

@socketio.on('change video')
def handle_change_video(data):
    print("in h_change_video")
    room_num = data.get('room')
    video_id = data.get('videoId')
    time = data.get('time')
    host = rooms.get("room-" + str(room_num), {}).get('host')

    prev_video_id = rooms.get("room-" + str(room_num), {}).get('currVideo', {}).get('yt')
    prev_time = time
    rooms["room-" + str(room_num)]['prevVideo']['yt'] = {'id': prev_video_id, 'time': prev_time}
    rooms["room-" + str(room_num)]['currVideo']['yt'] = video_id
    
    socketio.emit('changeVideoClient', {'videoId': video_id}, room="room-" + str(room_num))

    if data.get('prev'):
        print("call back needed here")
        socketio.emit("change video callback", True)

@socketio.on('send message')
def handle_send_message(data):
    encoded_msg = data.replace("<", "&lt;").replace(">", "&gt;")
    room_num = userrooms.get(request.sid)
    if room_num:
        socketio.emit('new message', {'msg': encoded_msg, 'user': users.get(request.sid)}, room="room-" + str(room_num))

@socketio.on('change time')
def handle_change_time(data):
    caller = data.get('id')
    time = data.get('time')
    socketio.emit('changeTime', {'time': time}, room=caller)

@socketio.on('sync host')
def handle_sync_host(data):
    room_num = userrooms.get(request.sid)
    if room_num:
        host = rooms.get("room-" + str(room_num), {}).get('host')
        if request.sid != host:
            print("sync host called by is not host")
            socketio.emit('getData', room=host)
        else:
            socketio.emit('syncHost', room_num, room=request.sid)

@socketio.on('player status')
def handle_player_status(data):
    print(data)

@socketio.on('get host data')
def handle_get_host_data(data):
    room_num = data.get('room')
    host = rooms.get("room-" + str(room_num), {}).get('host')
    if host:
        if data.get('currTime') is None:
            caller = request.sid
            socketio.emit('getPlayerData', {'room': room_num, 'caller': caller}, room=host)
        else:
            caller = data.get('caller')
            socketio.emit('compareHost', data, room=caller)

@socketio.on('auto sync')
def handle_auto_sync(data):
    import time

    def sync_host():
        while True:
            socketio.emit('syncHost')
            time.sleep(5)

    import threading
    threading.Thread(target=sync_host).start()























if __name__ == '__main__':
    socketio.run(app, debug=True)
