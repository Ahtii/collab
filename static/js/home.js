/* home jQuery */

$(document).ready(function(){
    var selected_user = "";
    var selected_room = "";
    $.get("/api/users/rooms", function(response){
        var rooms_list = response["rooms"]
        if (!jQuery.isEmptyObject(rooms_list)){
            var parent = $("#rooms ul");
            $.each(rooms_list, function(key, value){
                child = "<li>"+value["name"]+"</li>";
                parent.append(child);
            });
        }
    });
    $(document).on("click", "#rooms li", function(){
        var room = $(this).text();
        if (room){
            $("#auth h3 span").text(room);
            selected_user = "";
            selected_room = room;
        }
    });
    // change from public chat to personal chat
    $(document).on("click", "#left-sidebar ul a", function(){
       var user = $(this).text();
       $("#auth h3 span").text("chatting with "+user);
       selected_user = user;
       selected_room = "";
    });
    // change from personal to public chat
    $(document).on("click", "#public_chat", function(){
        var text = $("#auth h3 span").text();
        if (text != "public chat"){
            $("#auth h3 span").text("public chat");
            selected_user = "";
            selected_room = "";
        }
    });
    // create websocket
    var socket = new WebSocket("ws://localhost:8000/api/ws");
    socket.onmessage = function(event) {
        var parent = $("#messages");
        var data = JSON.parse(event.data);
        var sender = data['sender'];
        var message = data['message']
        if (message){
            var user = $("#cur_user").text();
            if (user == sender)
                sender = "you";
            var content = "<p><strong>"+sender+": </strong><br><span>"+message+"</span></p>";
            parent.append(content);
        } else if(sender) {
            if ($("#auth").hasClass("hide")){
                $("#auth").removeClass("hide");
                $("#not-auth").addClass("hide");
                $("#right-sidebar #cur_user").text(sender);
            }
            var parent = $("#left-sidebar ul");
            parent.empty();
            receivers = data['receivers'];
            $.each(receivers, function(index, receiver){
                console.log(receiver);
                if (sender != receiver){
                    var child = "<li> <a>"+receiver+"</a> </li>";
                    parent.append(child);
                }
            });
        } else {
            var room = data['room'];
            console.log(room);
            $("#rooms ul").append("<li>"+room+"</li>");
        }
    };
    // send message with websocket
    function sendMessage() {
        var input = document.getElementById("messageText");
        data = {
            "message": input.value,
            "receiver": selected_user,
            "room": selected_room
        };
        socket.send(JSON.stringify(data));
        input.value = '';
    }
    // submit form for chatting
    $("#chat-form").on("submit", function(e){
        e.preventDefault();
        //var socket = createSocket();
        sendMessage();
    });
    // logout the user
    $("#logout").on("click", function(){
        $.ajax({
            url: '/api/users',
            type: 'DELETE',
            success: function(response){
                window.location.href = "/"
            }
        });
    });
});