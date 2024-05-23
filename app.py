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

# also add route to handle invite
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
        print("after emit")

def updateQueueVideos(roomnum):
    room_name = "room-" + roomnum
    room = rooms.get(room_name)
    if room is not None:
        print("uqv if true")
        vidlist = room.get('queue', {})
        currPlayer = room.get('currPlayer', 0)
        print("currPlayer:", currPlayer)
        # socketio.emit('get vidlist', {'vidlist': vidlist, 'currPlayer': currPlayer})
        socketio.emit('get vidlist', {'vidlist': vidlist, 'currPlayer': currPlayer}, room=room_name)

@socketio.on("new room")
def handle_new_room(roomnum):

    host = None
    init = False

    if roomnum is None or roomnum == "":
        print("invalid room number handled to join.")
        roomnum = '1'
        
    room_name = "room-" + roomnum
    join_room(room_name)

    userrooms[request.sid] = roomnum

    if room_name not in rooms:
        print("new room created")
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
        print("no host in room so setting it up")
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
        print("request is not from the host")
        socketio.sleep(1)
        emit('getData', room=host)

        rooms[room_name]['users'].append(sidToUsername[request.sid])

    updateRoomUsers(roomnum)
    return True

@socketio.on('play video')
def handle_play_video(data):
    roomnum = data['room']
    print("hello pvc")
    socketio.emit('playVideoClient', room="room-" + roomnum)
    # socketio.emit('playVideoClient', {"success":True}) #this line change 

# @socketio.on('get video')
# def handle_get_video():
#     room_name = "room-" + userrooms[request.sid]
#     room = rooms.get(room_name)
#     print("inside handle get video", room)
#     if room is not None:
#         curr_video = room.get('currVideo', {}).get('yt')
#         print("curr_video:", curr_video)
#         emit('video sent', curr_video)
  
@socketio.on('disconnect')
def handle_disconnect():
    user_id = request.sid
    username = users.get(user_id)
    if username:
        users.remove(username)
    
    connections.remove(user_id)

    room_num = userrooms.get(user_id)
    room_name = "room-" + room_num
    room = rooms.get(room_name)

    if room:
        if user_id == room.get('host'):
            first_user_id = list(room.get('sockets'))[0]
            socketio.emit('autoHost', {'roomnum': room_num}, room=first_user_id)

        if username in room.get('users', []):
            room['users'].remove(username)
            update_room_users(room_num)

    del userrooms[user_id]

@socketio.on('sync video')
def handle_sync_video(data):
    print("handle_sync_vide:", data, request.sid)
    room_num = data.get('room')
    time = data.get('time')
    state = data.get('state')
    video_id = data.get('videoId')
    player_id = rooms.get("room-" + room_num, {}).get('currPlayer')
    socketio.emit('syncVideoClient', {'time': time, 'state': state, 'videoId': video_id, 'playerId': player_id}, room="room-" + room_num)


@socketio.on('play other')
def handle_play_other(data):
    room_num = data.get('room')
    socketio.emit('justPlay', room="room-" + room_num, skip_sid=request.sid)

@socketio.on('pause other')
def handle_pause_other(data):
    room_num = data.get('room')
    socketio.emit('justPause', room="room-" + room_num, skip_sid=request.sid)

@socketio.on('seek other')
def handle_seek_other(data):
    room_num = data.get('room')
    curr_time = data.get('time')
    socketio.emit('justSeek', {'time': curr_time}, room="room-" + room_num, skip_sid=request.sid)

@socketio.on('get video')
def handle_get_video():
    print("inside handle get video")
    room_num = userrooms.get(request.sid)
    if room_num:
        curr_video = rooms.get("room-" + room_num, {}).get('currVideo', {}).get('yt')
        socketio.emit('get video callback', curr_video, room="room-" + room_num)
    # else we can handle predefined curr_video to show

@socketio.on('change video')
def handle_change_video(data):
    print("inside handle change video:", data)
    room_num = data.get('room')
    video_id = data.get('videoId')
    time = data.get('time')
    host = rooms.get("room-" + room_num, {}).get('host')

    prev_video_id = rooms.get("room-" + room_num, {}).get('currVideo', {}).get('yt')
    prev_time = time
    rooms["room-" + room_num]['prevVideo']['yt'] = {'id': prev_video_id, 'time': prev_time}
    rooms["room-" + room_num]['currVideo']['yt'] = video_id
    
    socketio.emit('changeVideoClient', {'videoId': video_id}, room="room-" + room_num)

    if data.get('prev'):
        print("call back needed here")
        # callback()

@socketio.on('send message')
def handle_send_message(data):
    print("handle send message", data)
    encoded_msg = data.replace("<", "&lt;").replace(">", "&gt;")
    room_num = userrooms.get(request.sid)
    if room_num:
        print("inside handle send message", room_num)
        socketio.emit('new message', {'msg': encoded_msg, 'user': users.get(request.sid)}, room="room-" + room_num)

@socketio.on('change time')
def handle_change_time(data):
    caller = data.get('id')
    time = data.get('time')
    socketio.emit('changeTime', {'time': time}, room=caller)

@socketio.on('sync host')
def handle_sync_host(data):
    room_num = userrooms.get(request.sid)
    print("inside handle_sync_host")
    if room_num:
        host = rooms.get("room-" + room_num, {}).get('host')
        if request.sid != host:
            print(f"handle_sync_host: req:{request.sid}, host:{host}")
            socketio.emit('getData', room=host)
        else:
            print(f"handle_sync_host: ..reqfromhost.. req:{request.sid}, host:{host}")
            socketio.emit('syncHost', room=request.sid)

@socketio.on('player status')
def handle_player_status(data):
    print(data)

@socketio.on('get host data')
def handle_get_host_data(data):
    room_num = data.get('room')
    host = rooms.get("room-" + room_num, {}).get('host')
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
