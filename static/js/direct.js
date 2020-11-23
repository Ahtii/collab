/* home jQuery */
$(document).ready(function(){
    var selected_room = "";
    var url = window.location.href;
    var receiver = url.slice(url.indexOf('=') + 1);
    var user = "", socket;
    $("h3 span").text("chatting with "+receiver);
    $.get("/api/user", function(response){
         user = response["user"];
         if (user){
            if ($("#auth").hasClass("hide")){
                $("#auth").removeClass("hide");
                $("#not-auth").addClass("hide");
                $("#cur_user").text(user);
            }
            // create websocket
            socket = new WebSocket("ws://localhost:8000/api/user-chat/"+receiver);
            socket.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var sender = data['sender'];
                //var cur_user = data['cur_user'];
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
                } else if (room){
                    $("#rooms ul").append("<li>"+room+"</li>");
                }
            };
         }
    });
    // send message with websocket
    function sendMessage() {
        var input = document.getElementById("messageText");
        data = {
            "message": input.value,
            "receiver": receiver,
            "room": selected_room
        };
        socket.send(JSON.stringify(data));
        input.value = '';
    }
    // submit form for chatting
    $("#chat-form").on("submit", function(e){
        e.preventDefault();
        sendMessage();
    });
});