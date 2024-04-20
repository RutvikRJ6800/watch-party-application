
function playOther(roomnum) {
    socket.emit('play other', {
        room: roomnum
    });
}

socket.on('justPlay', function(data) {
    console.log("currPlayer")
    player.playVideo()
});

function pauseOther(roomnum) {
    socket.emit('pause other', {
        room: roomnum
    });
}

socket.on('justPause', function(data) {
    console.log("hiIamPausing!")
    player.pauseVideo()
});

function seekOther(roomnum, currTime) {
    socket.emit('seek other', {
        room: roomnum,
        time: currTime
    });
}


socket.on('justSeek', function(data) {
    console.log("Seeking Event!")
    currTime = data.time
    var clientTime = player.getCurrentTime();
    if (clientTime < currTime - .2 || clientTime > currTime + .2) {
        player.seekTo(currTime);
        player.playVideo()
    }
});
