/* home jQuery */
$(document).ready(function(){
    var url = window.location.href;
    var receiver = url.slice(url.indexOf('=') + 1);
    var user = "", socket;
    var file = null;
    $("h3 span").text("chatting with "+receiver);
    $.get("/api/user", function(response){
         user = response["user"];
         if (user){
            // create websocket
            socket = new WebSocket("ws://localhost:8000/api/user-chat/"+receiver);
            socket.onmessage = function(event) {
                var data = JSON.parse(event.data);
                var sender = data['sender'];
                var author = data['author'];
                var message = data['message'];
                var date = data['date'];
                var file = data['file'];
                var parent = $("#messages");
                var file_url = "";
                if (message || file){
                    if (user == author)
                        author = "you";
                    if (file)
                        file_url = "<br><a href='"+file+"'>"+data['filename']+"</a>";
                    console.log("file name:");
                    console.log(data['filename']);
                    var content = "<p><strong>"+author+": </strong> &nbsp; <span class='date'>"+date+"</span><br><span>"+message+"</span>"+file_url+"</p>";
                    parent.append(content);
                }
            };
         }
    });
    // send message with websocket
    function sendMessage() {
        var input = document.getElementById("messageText");
        console.log(file);
        data = {
            "message": input.value,
            "receiver": receiver
        };
        console.log(file);
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
            } else
                $("#err-msg").text("Only files less than 5MB allowed.");
        } else {
            console.log(JSON.stringify(data));
            socket.send(JSON.stringify(data));
        }
        input.value = '';
    }
    // submit form for chatting
    $("#chat-form").on("submit", function(e){
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
        file = e.target.files[0];
    });
});