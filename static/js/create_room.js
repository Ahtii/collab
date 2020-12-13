
$(document).ready(function(){
    var current_user;
    var uid;
    var socket;
    // get current user
    $.get("/api/user", function(response){
         current_user = response["user"]
         if (current_user){
            uid = response['id'];
            // get all users
            $.get("/api/users", function(response){
                var users_list = response["users"]
                if (!jQuery.isEmptyObject(users_list)){
                    var parent = $("#participants ul");
                    $.each(users_list, function(key, value){
                        if (current_user != value){
                            child = "<li> <a>"+value+"</a> </li>";
                            parent.append(child);
                        }
                    });
                    // websockets
                    // socket = new WebSocket("ws://localhost:8000/api/room-creation");
                    // socket.onmessage = function(event) {
                    //     // var data = JSON.parse(event.data);
                    //     // var mid = data['id'];
                    //     // var sender = data['sender'];
                    //     // var author = data['author'];
                    //     // var message = data['message'];
                    //     // var ist_date = data['ist_date'];
                    //     // var est_date = data['est_date'];
                    //     // var file = data['file'];
                    //     // var parent = $("#messages");
                    //     // var file_url = "";
                    //     // if (message || file){
                    //     //     if (user == author)
                    //     //         author = "you";
                    //     //     if (file){
                    //     //         var full_path = file.split("/");
                    //     //         var file_owner = full_path[full_path.length - 3];
                    //     //         var file_name = full_path[full_path.length - 1];    
                    //     //         file_url = "<br><a href='/preview-file?user="+file_owner+"&file="+file_name+"'>"+data['filename']+"</a>";
                    //     //     }                            
                    //     //     console.log("file name:");
                    //     //     console.log(data['filename']);
                    //     //     var mid_html = "<input class='mid' value="+mid+" hidden/>";
                    //     //     var content = "<p>"+mid_html+"<strong>"+author+": </strong> &nbsp; <span class='date'>"+ist_date+" &nbsp; "+est_date+"</span><br><span>"+message+"</span>"+file_url+"</p>";
                    //     //     parent.append(content);
                    //     // }
                    //     var room = data['room'];
                    //     if (room){
                    //         var room_name_html = "<li>"+room+"</li>";
                    //         $("#rooms ul").append(room_name_html);
                    //     }
                    // };
                }
            });            
         }
    });
    sel_participants = [];
    // collected selected participants
    $(document).on("click", "#participants li", function(){
        var parent = $("#sel-participants ul");
        var selected_participant = $(this).text();
        var found = false;
        var target = $("#sel-participants li");
        $.each(target, function(idx, ele){
            if (selected_participant == $(ele).text()){
                found = true;
                return false;
            }
        });
        if (!found){
            html = "<li>"+selected_participant+"</li>"
            $(parent).append(html);
            sel_participants.push(selected_participant);
        }
    });
    // create room
    $("#room-form").on("submit", function(e){
        e.preventDefault();
        data = {
            "name": $("#room-name").val(),
            "description": $("#room-desc").val(),
            "participants": sel_participants
        };
        $.post("/api/user/"+uid+"/rooms",JSON.stringify(data), function(response){
            var error = response["error"];
            if (error){
                $("#err").text(error);
            } else {
                //socket.send(JSON.stringify({"room": data['room']}));
                window.location.href = "/"
            }
        });
    });
});