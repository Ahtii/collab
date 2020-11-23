/* home jQuery */
$(document).ready(function(){
    var selected_user = "";
    var selected_room = "";
    var user = "", socket;
    $.get("/api/user", function(response){
         user = response["user"];
         if (user){
            if ($("#auth").hasClass("hide")){
                $("#auth").removeClass("hide");
                $("#not-auth").addClass("hide");
                $("#cur_user").text(user);
            }
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
            // create websocket
            socket = new WebSocket("ws://localhost:8000/api/user-connect");
            socket.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var sender = data['sender'];
                //var cur_user = data['cur_user'];
                var author = data['author'];
                var message = data['message'];
                var date = data['date'];
                var room = data['room'];
                var parent = $("#messages");
                if(sender) {
                    var parent = $("#online-users ul");
                    parent.empty();
                    receivers = data['receivers'];
                    $.each(receivers, function(index, receiver){
                        if (sender != receiver){
                            var child = "<li> <a>"+receiver+"</a></li>";
                            parent.append(child);
                        }
                    });
                }
                if (message){
                    $("#no-message").addClass("hide");
                    $("#messages").removeClass("hide");
                    if (user == author)
                        author = "you";
                    var content = "<p><strong>"+author+"</strong>:  &nbsp; <span class='date'>"+date+"</span><br><span>"+message+"</span></p>";
                    parent.append(content);
                }
            };
         }
    });
    $(document).on("click", "#messages p", function(){
        var user = $(this).children("strong").text();
        window.location.href = "/direct?user="+user;
    });
    $(document).on("click", "#rooms li", function(){
        var room = $(this).text();
        if (room)
           window.location.href = "/rooms?room="+room;
    });
    // change from public chat to personal chat
    $(document).on("click", "#online-users ul a", function(){
       var user = $(this).text();
       socket.close();
       window.location.href = "/direct?user="+user;
    });
    //send message with websocket
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