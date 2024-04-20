function playVideo(roomnum) {
    socket.emit('play video', {
        room: roomnum
    });

}

function syncVideo(roomnum) {
    var currTime = 0
    var state
    var videoId = id

    currTime = player.getCurrentTime();
    state = playerStatus
    socket.emit('sync video', {
        room: roomnum,
        time: currTime,
        state: state,
        videoId: videoId
    });

    
}

function getTime() {
    return player.getCurrentTime();
}

function seekTo(time) {
    player.seekTo(time)
    player.playVideo()
}

function idParse(videoId) {
    if (videoId.includes("https://") || videoId.includes("http://") || videoId.includes(".com/")) {
        if (videoId.includes("youtu.be")) {
            var myRegex = /.+youtu\.be\/([A-Za-z0-9\-_]+)/g
            var match = myRegex.exec(videoId)
            if (match != null) {
                return match[1]
            }
        } else {
          var myRegex = /.+watch\?v=([A-Za-z0-9\-_]+)/g
          var match = myRegex.exec(videoId)
          if (match != null) {
              return match[1]
          }
        }
        videoId = "invalid"    
    }
    return videoId
}

function playlistParse(videoId) {
    if (videoId.includes("https://") || videoId.includes("http://") || videoId.includes(".com/")) {
        var myRegex = /.+&list=([A-Za-z0-9\-_]+)/g
        var match = myRegex.exec(videoId)
        if (match != null) {
            return match[1]
        }    
    }
    return "invalid"
}


function changeVideoParse(roomnum) {
  var videoId = document.getElementById("inputVideoId").value
  changeVideo(roomnum, videoId)
}

function changeVideo(roomnum, rawId) {
    var videoId = idParse(rawId)

    if (videoId != "invalid") {
        var time = getTime()
        socket.emit('change video', {
            room: roomnum,
            videoId: videoId,
            time: time
        });
    } else {
        invalidURL()
    }
}

function changeVideoId(roomnum, id) {
    document.getElementById("inputVideoId").innerHTML = id;
    socket.emit('change video', {
        room: roomnum,
        videoId: id
    });
}

socket.on('getData', function(data) {
    socket.emit('sync host', {});
});

function changeSinglePlayer(playerId) {
    return new Promise((resolve, reject) => {
        if (playerId != currPlayer) {
            socket.emit('change single player', {
                playerId: playerId
            });
        }
        resolve("socket entered change single player function")
    })
}



var roomnum = 1
var id = "tXha7F48HyU"

socket.on('playVideoClient', function(data) {
    play()
});

socket.on('pauseVideoClient', function(data) {
    player.pauseVideo();
});

socket.on('syncVideoClient', function(data) {
    var currTime = data.time
    var state = data.state
    var videoId = data.videoId
    var playerId = data.playerId
    if (currPlayer != playerId) {
        changeSinglePlayer(playerId)
    } else {
        var clientTime = player.getCurrentTime();
        if (true || clientTime < currTime - .1 || clientTime > currTime + .1) {
            player.seekTo(currTime);
        }
        if (state == 2) {
            console.log("paused?")
            player.pauseVideo();
        }
        else {
            player.playVideo();
        }
        
    }

});

socket.on('changeVideoClient', function(data) {
    var videoId = data.videoId;
    console.log("video id is: " + videoId)

    socket.emit('get video', function(id) {
        console.log("it really is " + id)
        videoId = id
        id = videoId
        player.loadVideoById(videoId);
        
    })

    setTimeout(function() {
        console.log("resyncing with host after video change")
        socket.emit('sync host', {});
    }, 1000);

});

socket.on('changeTime', function(data) {
    var time = data.time
    player.seekTo(time);
});
