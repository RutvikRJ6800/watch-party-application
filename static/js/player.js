var currPlayer = 0

socket.on('getPlayerData', function(data) {
    var roomnum = data.room
    var caller = data.caller

    var currTime = player.getCurrentTime()
    var state = playerStatus
    socket.emit('get host data', {
                room: roomnum,
                currTime: currTime,
                state: state,
                caller: caller
            });
});

