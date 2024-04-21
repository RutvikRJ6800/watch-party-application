var host = false
var notifyfix = false

socket.on('setHost', function(data) {
    notifyfix = true
    console.log("You are the new host!")
    host = true
});
socket.on('unSetHost', function(data) {
    console.log("Unsetting host")
    host = false
});

socket.on('getData', function(data) {
    console.log("Hi im the host, you called?")
    socket.emit('sync host', {});
});

socket.on('syncHost', function(data) {
    syncVideo(roomnum)
});

function changeHost(roomnum) {
    if (!host){
        socket.emit('change host', {
            room: roomnum
        });
        socket.emit('notify alerts', {
            alert: 1,
            user: username
        })
    }
}
socket.on('autoHost', function(data) {
    changeHost(data.roomnum)
})

function disconnected() {
    if (notifyfix) {
        disconnectedAlert()
    } else {
        notifyfix = true
    }
}

function getHostData(roomnum) {
    socket.emit('get host data', {
        room: roomnum
    });
}

socket.on('compareHost', function(data) {
    var hostTime = data.currTime
    var hostState = data.state

    var currTime = player.getCurrentTime()
    var state = playerStatus

    console.log("curr: " + currTime + " Host: " + hostTime)
    if (currTime < hostTime - 2 || currTime > hostTime + 2) {
        disconnected()
    }
    
});

function test() {
    document.getElementById('player').src = document.getElementById('player').src + '&controls=0'
}


socket.on('hostControls', function(data) {
    if (!host) {
        console.log("SOURCE: " + document.getElementById('player').src)
        document.getElementById('player').src = document.getElementById('player').src.replace("&controls=1", "&controls=0")
        console.log("POSTSOURCE: " + document.getElementById('player').src)

    }
    else {
        document.getElementById('player').src = document.getElementById('player').src.replace("&controls=0", "&controls=1")
    }
});

