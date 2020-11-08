/* home jQuery */

$(document).ready(function(){
    var current_user = null;
    var selected_user = "";
    // get user if logged in
    $.get("/api/current_user", function(response){
         current_user = response["user"]
         if (current_user){
            $("#auth").removeClass("hide");
            $("#not-auth").addClass("hide");
            $("#right-sidebar #cur_user").text(current_user);
            // get list of online users
            $.get("/api/online_users", function(response){
                var users_list = response["users"]
                if (!jQuery.isEmptyObject(users_list)){
                    var parent = $("#left-sidebar ul");
                    $.each(users_list, function(key, value){
                        if (current_user != value){
                            child = "<li> <a>"+value+"</a> </li>";
                            parent.append(child);
                        }
                    });
                }
            });
         }
    });
    // change from one public chat to personal
    $(document).on("click", "ul a", function(){
       var user = $(this).text();
       $("#auth h3 span").text(user);
       selected_user = user;
    });
    // change from personal to public chat
    $(document).on("click", "#public_chat", function(){
        var text = $("#auth h3 span").text();
        if (text != "public chat"){
            $("#auth h3 span").text("public chat");
            selected_user = "";
        }
    });
    // create websocket
    var socket = new WebSocket("ws://localhost:8000/api/ws");
    socket.onmessage = function(event) {
        var parent = $("#messages");
        var data = event.data;
        var index = data.indexOf(":");
        var sender = data.substring(0, index);
        if (sender == current_user)
            sender = "you";
        sender = sender + ":"
        var message = data.substring(index + 1, data.length);
        var content = "<p><strong>"+sender+"</strong><br><span>"+message+"</span></p>";
        parent.append(content);
    };
    // send message with websocket
    function sendMessage() {
        var input = document.getElementById("messageText");
        data = {
            "message": input.value,
            "client": selected_user
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
        $.post("/api/logout", function(response){
            window.location.href = "/"
        });
    });
});