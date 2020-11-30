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
                var receiver = data['receiver'];
                var author = data['author'];
                var message = data['message'];
                var date = data['date'];
                var room = data['room'];
                var file = data['file'];
                var file_url = "";
                var parent = $("#messages");
                console.log(data);
                if(sender) {
                    var parent = $("#online-users ul");
                    parent.empty();
                    var receivers = data['receivers'];
                    $.each(receivers, function(index, receiver){
                        if (sender != receiver){
                            var child = "<li> <a>"+receiver+"</a></li>";
                            parent.append(child);
                        }
                    });
                }
                if (message || file){
                    $("#no-message").addClass("hide");
                    $("#messages").removeClass("hide");
                    if (file){
                        var full_path = file.split("/");
                        var file_owner = full_path[full_path.length - 2];
                        var file_name = full_path[full_path.length - 1];    
                        file_url = "<br><a href='/preview-file?user="+file_owner+"&file="+file_name+"'>"+data['filename']+"</a>";
                    }                            
                    var user_tag = author;
                    if (user == author){
                        author = "you";
                        user_tag = receiver;
                    }
                    var messages = $("#messages p");
                    var no_match = true;
                    $.each(messages, function(index, msg){
                        console.log(index);
                        var user_msg = $(msg).children("strong").text();
                        if (user_msg == user_tag){
                            $(msg).empty();
                            var notifier = "<i class='badge badge-primary notifier'>1</i>";
                            var content = "<strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+date+"</span> &nbsp;"+notifier+"<br><span>"+author+"</span>: <span>"+message+"</span>"+file_url;
                            $(msg).addClass("highlight");
                            $(msg).append(content);
                            no_match = false;
                            return false;
                        }
                    });
                    if (no_match){
                        var content = "<p><strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+date+"</span><br><span>"+author+"</span>: <span>"+message+"</span>"+file_url+"</p>";
                        parent.append(content);
                    }
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