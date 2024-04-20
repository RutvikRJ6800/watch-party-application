# app.py
from flask import Flask, render_template, request, redirect, url_for
from flask_socketio import SocketIO, emit, join_room, leave_room
import requests

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SECRET_KEY'] = 'your_secret_key'
socketio = SocketIO(app)

rooms = []
users = {} # maps sid to username
userrooms = {}



@app.route('/')
def index():
    return render_template('index.html')

@socketio.on("new user")
def handle_new_user(username):
    print(f"new user {username} is here")
    users[username] = request.sid

@app.route('/create_room', methods=['POST'])
def create_room():
    room_id = request.form['room_id']
    if room_id in rooms:
        return redirect(url_for('index'))
    rooms[room_id] = {'host': request.sid, 'video_link': None, 'video_timestamp': 0, 'users': set()}
    return redirect(url_for('watch', room_id=room_id))

@app.route('/join_room/<string:room_id>')
def join_room(room_id):
    if room_id not in rooms:
        return redirect(url_for('index'))
    return render_template('room.html', room_id=room_id)

@socketio.on('join')
def handle_join(data):
    room_id = data['room_id']
    join_room(room_id)
    rooms[room_id]['users'].add(request.sid)
    emit('update_users', {'users': list(rooms[room_id]['users'])}, room=room_id)

@socketio.on('leave')
def handle_leave(data):
    room_id = data['room_id']
    leave_room(room_id)
    rooms[room_id]['users'].remove(request.sid)
    emit('update_users', {'users': list(rooms[room_id]['users'])}, room=room_id)

@socketio.on('sync')
def handle_sync(data):
    room_id = data['room_id']
    timestamp = data['timestamp']
    rooms[room_id]['video_timestamp'] = timestamp
    emit('sync_video', {'timestamp': timestamp}, room=room_id, include_self=False)

@socketio.on('chat_message')
def handle_chat_message(data):
    room_id = data['room_id']
    emit('chat_message', data, room=room_id)

    
@socketio.on("new room")
def handle_new_room(roomno):
    userrooms[request.sid] = roomno

    host = None
    init = False

    # username = session['username']
    # room = data['room']
    # join_room(room)
    # send(username + ' has entered the room.', to=room)


    if(roomno == None or roomno == ""):
        roomno = '1'
        userrooms[request.sid] = '1'

    if roomno not in rooms:
        rooms.append(roomno)

    print("hereh")
    socketio.send()

    

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
