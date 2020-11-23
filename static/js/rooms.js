/* home jQuery */
$(document).ready(function(){
    var selected_room = "";
    var url = window.location.href;
    var room = url.slice(url.indexOf('=') + 1);
    var user = "", socket;
    room = room.replace("%20", " ");
    $("h3 span").text(room);
    $.get("/api/user", function(response){
         user = response["user"];
         if (user){
            // create websocket
            socket = new WebSocket("ws://localhost:8000/api/room-chat/"+room);
            socket.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var author = data['author'];
                var message = data['message'];
                var date = data['date'];
                var room = data['room'];
                var parent = $("#messages");
                if (message){
                    if (user == author)
                        author = "you";
                    var content = "<p><strong>"+author+": </strong> &nbsp; <span class='date'>"+date+"</span><br><span>"+message+"</span></p>";
                    parent.append(content);
                }
            };
         }
    });
    // send message with websocket
    function sendMessage() {
        var input = document.getElementById("messageText");
        data = {
            "message": input.value,
            "room": room,
            "user": user
        };
        socket.send(JSON.stringify(data));
        input.value = '';
    }
    // submit form for chatting
    $("#rooms-form").on("submit", function(e){
        e.preventDefault();
        //var socket = createSocket();
        sendMessage();
    });
});