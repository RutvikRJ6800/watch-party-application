
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


// ===============================


// Handle form submission to send messages
// document.getElementById("messageForm").addEventListener("submit", function(event) {
//     event.preventDefault();
//     let messageInput = document.getElementById("message");
//     let message = messageInput.value.trim();
//     if (message !== "") {
//         sendMessage(message);
//         messageInput.value = "";
//     }
// });

// // Function to send a message
// function sendMessage(message) {
//     // Add message to the chat container
//     let chatContainer = document.getElementById("chat");
//     let messageElement = document.createElement("div");
//     messageElement.classList.add("chat-message");
//     messageElement.innerHTML = `
//         <img src="person_icon.png" class="message-icon">
//         <div class="message-text">${message}</div>
//     `;
//     chatContainer.appendChild(messageElement);
//     // Scroll to the bottom of the chat container
//     chatContainer.scrollTop = chatContainer.scrollHeight;
// }

color_list = [
    "#3D52D5",
    "#B0B15A",
    "#4CBAF9",
    "#F06FA2",
    "#7C48A4",
    "#F05E49",
    "#6AC27B",
    "#AC9CF5",
    "#7B6D3F",
    "#D8C70E"
  ]

function getUserInfo(userIndex) {
    // You can implement this function to fetch user info from your data structure
    // For now, we'll return a hardcoded object
    // You should modify this to fetch user info from your actual data structure
    return {
        image: userIndex + ".png", // Assuming image files are named as "0.jpeg", "1.jpeg", etc.
        nameColor: color_list[userIndex] // Hardcoded name color for demonstration
    };
}

function addMessage(data, userIndex) {
    
    if (userIndex !== undefined) {
        var user = getUserInfo(userIndex); // Fetch user info
        if (user) {
            var messageWell = document.createElement("div");
            messageWell.classList.add("well", "well-sm", "message-well");
            
            var userImage = document.createElement("img");
            userImage.src = "../static/img/" + user.image; // Set image source
            userImage.style.width = "25px"; // Set image width
            userImage.style.height = "25px";
            userImage.style.borderRadius = "50%";
            userImage.classList.add("user-image");
            
            
            
            var userNameElement = document.createElement("strong");
            userNameElement.style.color = user.nameColor; // Set name color
            userNameElement.textContent = data.user ;
            userNameElement.style.marginLeft = "10px";
            
            var messageText = document.createElement("div");
            messageText.textContent = data.msg;
            messageText.style.marginLeft = "35px";

            messageWell.appendChild(userImage);
            messageWell.appendChild(userNameElement);
            // messageWell.appendChild(document.createTextNode(": ")); // Add colon separator
            messageWell.appendChild(messageText);

            // Append message well to chat container
            var chatContainer = document.getElementById("chat");
            chatContainer.appendChild(messageWell);
            chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom
        }
    }
}

function appendMessageToChat(data) {
    
    var messageWell = document.createElement("div");
    messageWell.classList.add("well", "well-sm", "message-well");
    
    var messageText = document.createElement("div");
    messageText.textContent = data.msg;
    messageText.style.marginLeft = "35px";
    
    messageWell.appendChild(messageText);
    var chatContainer = document.getElementById("chat");
    chatContainer.appendChild(messageWell);
    chatContainer.scrollTop = chatContainer.scrollHeight; // Scroll to bottom
}

document.getElementById('sendButton').draggable = false;



