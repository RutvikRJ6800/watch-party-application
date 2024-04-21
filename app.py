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



@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("new user")
def handle_new_user(username):
    print(f"new user {username} is here")
    users[username] = request.sid
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
        # socketio.emit('get vidlist', {'vidlist': vidlist, 'currPlayer': currPlayer})
        socketio.emit('get vidlist', {'vidlist': vidlist, 'currPlayer': currPlayer}, room=room_name)

@socketio.on("new room")
def handle_new_room(roomnum):
    # userrooms[request.sid] = roomno

    # host = None
    # init = False

    # # username = session['username']
    # # room = data['room']
    # # join_room(room)
    # # send(username + ' has entered the room.', to=room)


    # if(roomno == None or roomno == ""):
    #     roomno = '1'
    #     userrooms[request.sid] = '1'

    # if roomno not in rooms:
    #     rooms.append(roomno)
    #     socketio.send(request.sid)
    #     host = request.sid
    #     init = True

    #     socketio.emit('setHost') # send this in front end
    # else:
    #     host = roomToHost[roomno]

    

    # print("roomno", roomno)
    # socketio.send()
    # print(roomnum, type(roomnum))
    room_name = "room-" + roomnum
    join_room(room_name)

    userrooms[request.sid] = roomnum

    host = None
    init = False

    if roomnum is None or roomnum == "":
        roomnum = '1'
        userrooms[request.sid] = '1'

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

@socketio.on('get video')
def handle_get_video():
    room_name = "room-" + userrooms[request.sid]
    room = rooms.get(room_name)
    if room is not None:
        curr_video = room.get('currVideo', {}).get('yt')
        emit('video sent', curr_video)
  

'''
socket.on('new room', function(data, callback) {
        socket.roomnum = data;

        userrooms[socket.id] = data

        var host = null
        var init = false

        if (socket.roomnum == null || socket.roomnum == "") {
            socket.roomnum = '1'
            userrooms[socket.id] = '1'
        }

        if (!rooms.includes(socket.roomnum)) {
            rooms.push(socket.roomnum);
        }

        if (io.sockets.adapter.rooms['room-' + socket.roomnum] === undefined) {
            socket.send(socket.id)
            host = socket.id
            init = true

            socket.emit('setHost');
        } else {
            host = io.sockets.adapter.rooms['room-' + socket.roomnum].host
        }

        socket.join("room-" + socket.roomnum);

        if (init) {
            io.sockets.adapter.rooms['room-' + socket.roomnum].host = host
            io.sockets.adapter.rooms['room-' + socket.roomnum].currPlayer = 0
            io.sockets.adapter.rooms['room-' + socket.roomnum].currVideo = {
                yt: 'tXha7F48HyU',
            }
            io.sockets.adapter.rooms['room-' + socket.roomnum].prevVideo = {
                yt: {
                    id: 'tXha7F48HyU',
                    time: 0
                },
                
            }

            io.sockets.adapter.rooms['room-' + socket.roomnum].hostName = socket.username
            io.sockets.adapter.rooms['room-' + socket.roomnum].users = [socket.username]
            io.sockets.adapter.rooms['room-' + socket.roomnum].queue = {
                yt: []
            }
        }

        io.sockets.in("room-" + socket.roomnum).emit('changeHostLabel', {
            username: io.sockets.adapter.rooms['room-' + socket.roomnum].hostName
        })

        updateQueueVideos()

        var currVideo = io.sockets.adapter.rooms['room-' + socket.roomnum].currVideo.yt

        socket.emit('changeVideoClient', {
            videoId: currVideo
        });

        if (socket.id != host) {
            

            setTimeout(function() {
                socket.broadcast.to(host).emit('getData');
            }, 1000);
            
            io.sockets.adapter.rooms['room-' + socket.roomnum].users.push(socket.username)

            
        } 

        updateRoomUsers(socket.roomnum)

    });

'''
























if __name__ == '__main__':
    socketio.run(app, debug=True)
