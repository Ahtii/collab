/* home jQuery */
$(document).ready(function(){
    var selected_room = "";
    var url = window.location.href;
    var room = url.slice(url.indexOf('=') + 1);
    var user = "", socket;
    var file = null;
    room = room.replaceAll("%20", " ");
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
                var file = data['file'];
                var file_url = "";
                var parent = $("#messages");
                if (message || file){
                    if (user == author)
                        author = "you";
                    if (file){
                        var full_path = file.split("/");
                        var file_owner = full_path[full_path.length - 2];
                        var file_name = full_path[full_path.length - 1];    
                        file_url = "<br><a href='/preview-file?user="+file_owner+"&file="+file_name+"'>"+data['filename']+"</a>";
                    }                            
                    var content = "<p><strong>"+author+": </strong> &nbsp; <span class='date'>"+date+"</span><br><span>"+message+"</span>"+file_url+"</p>";
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
        if (file){
            var file_data = {
                "filename": file['name'],
                "type": file['type'],
                "size": file['size']
            };
            console.log("file name");
            console.log(file['name']);
            if (file_data['size'] <= 5000000){
                data["file"] = file_data;
                console.log(JSON.stringify(data));
                socket.send(JSON.stringify(data));
                socket.send(file);
                $("#selected-file").text("");
            } else
                $("#err-msg").text("Only files less than 5MB allowed.");
        } else {
            console.log(JSON.stringify(data));
            socket.send(JSON.stringify(data));
        }
        input.value = '';
    }
    // submit form for chatting
    $("#rooms-form").on("submit", function(e){
        e.preventDefault();
        sendMessage();
    });
     // open file dialog
    $("#upload").on("click", function(){
        // code to send file to server
        $("#file").click();
    });
    // get opened file
    $("#file").on("change", function(e){
        // code to send file to server
        $("#err-msg").text("");
        $("#selected-file").text("");
        file = e.target.files[0];
        $("#selected-file").text(file["name"]);
    });
});