

/* chat jQuery */
$(document).ready(function(){
    var selected_user, file;
    var selected_room = "", unseen_messages = [];
    var user = "", socket;
    var uid;    

    $.get("/api/user", function(response){
        user = response["user"];     
        if (user){
           var name = response['full_name'];
           $(".active-user").text(name);
           uid = response['id'];
           $.get("/api/user/"+uid+"/rooms", function(response){
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
           var protocol = window.location.protocol === "http:" ? "ws://" : "wss://";
           var host = window.location.host;
           var api_path = "/chat";
           var full_address = protocol+host+api_path;
           console.log(window.location.protocol);
           socket = new WebSocket(full_address);
           socket.onmessage = function(event) {
               var data = JSON.parse(event.data);
               var user_state = data['state'];
               var loaded = data['completed']
               var mid = data['id'];
               var online_users = data["online_users"];
               var receiver = data['receiver'];
               var stranger = data['stranger'];
               var author = data['author'];
               var message = data['message'];
               var ist_date = data['ist_date'];
               var est_date = data['est_date'];
               var last_message = data['last_message'];
               var room = data['room'];
               var file = data['file'];
               var file_url = "";                 
                if (online_users) {
                    var direct_msg_list = $("#direct-msg-list li");                                                            
                    $.each(direct_msg_list, function(index, msg){                                                                        
                        var target_item = $(msg).find(".state"); 
                        var username = $(msg).find(".username-holder").text();                                                                                          
                        if ($(target_item).hasClass("online")){
                            $(target_item).removeClass("online");
                            $(target_item).addClass("offline");                                                     
                        }                                                    
                        $.each(online_users, function(index, online_user){
                            if (user != online_user['username']){  
                                if (username == online_user['username']){                                    
                                    if ($(target_item).hasClass("offline")){
                                        $(target_item).removeClass("offline");
                                        $(target_item).addClass("online");
                                    }
                                }
                            }
                        });  
                        var panel_username = $("#chatPanel .name").find(".username-holder").text();                        
                        if (username == panel_username){
                            console.log(panel_username);
                            var state = "offline";
                            if ($(msg).find(".state").hasClass("online"))
                                state = "online";
                            var classes = $(msg).find(".state").attr("class");
                            $("#chatPanel .under-name").find("i").removeClass();
                            $("#chatPanel .under-name").find("i").addClass(classes);
                            $("#chatPanel .under-name").find("span").text(state);                                                                            
                        }                                               
                    });                                  
                }  
                var show_notification = false;
                // code to show message
                if (!room && (message || file)){                    
                    if (file){
                            var full_path = file.split("/");
                            var file_owner = full_path[full_path.length - 3];
                            var file_name = full_path[full_path.length - 1];    
                            file_url = "<br><a href='/preview-file?user="+file_owner+"&file="+file_name+"'>"+data['filename']+"</a>"; 
                    }                                          
                    var displayname = author["fullname"];
                    var user_tag = displayname;
                    var display_username = author['username'];
                    if (user == display_username){   
                        displayname = "You";
                        display_username = receiver['username'];
                        user_tag = receiver["fullname"];                       
                    }                    
                    var username_holder = "<span class='hide username-holder'>"+display_username+"</span>";                                                
                    if (last_message){                    
                        var content = "<li class='list-group-item list-group-item-action'>\
                                        <div class='row'>\
                                            <div class='col-2 col-md-2'><img src='/static/media/images/maleuser.png' class='profile-pic'/></div>\
                                            <div class='col-md-10 col-10' style='cursor: pointer;'>\
                                                "+username_holder+"\
                                                <div class='name'><i class='fa fa-circle state offline'></i>&nbsp;<span>"+user_tag+"</span></div>\
                                                <div class='under-name'> "+displayname+": &nbsp; "+message+"&nbsp;"+file_url+"</div>\
                                            </div>\
                                        </div>\
                                    </li>"; 
                        $("#direct-msg-list").append(content);    
                    } else {
                        var panel_selected_user = $("#chatPanel .name").find(".username-holder").text();
                        // decide position of message box
                        var content;
                        if (user == author["username"]){
                            content = "<div class='row'>\
                                <div class='col-1 col-sm-1 col-md-1'>\
                                    <img src='/static/media/images/maleuser.png' class='chat-pic'/>&nbsp;\
                                </div>\
                                <div class='col-6 col-sm-7 col-md-7'>\
                                    <p class='received-msg'>\
                                        <strong>"+displayname+"</strong><span class='timestamp float-right'>"+ist_date+" &nbsp; "+est_date+"</span><br>\
                                        <span>"+message+"</span>\
                                        "+file_url+"\
                                    </p>\
                                </div>\
                            </div>";
                        } else if (panel_selected_user == author['username']) {
                            content = "<div class='row justify-content-end'>\
                                <div class='col-6 col-sm-7 col-md-7'>\
                                    <p class='sent-msg float-right'>\
                                        <strong>"+displayname+"</strong><span class='timestamp float-right'>"+ist_date+" &nbsp; "+est_date+"</span><br>\
                                        <span>"+message+"</span>\
                                        "+file_url+"\
                                    </p>\
                                </div>\
                                <div class='col-1 col-sm-1 col-md-1'>\
                                    <img src='/static/media/images/maleuser.png' class='chat-pic'/>&nbsp;\
                                </div>\
                            </div>";
                        } else {
                             show_notification = true;                              
                        }   
                        if (content)
                            $("#messages").append(content);            
                    }                               
                }
                if (stranger){  
                    var match = false;                     
                    $.each($("#direct-msg-list li"), function(index, value){
                        if ($(this).find(".username-holder").text() == stranger["username"]){
                            match = true;
                            return;
                        }
                    });           
                    if (!match && stranger["username"] != user){
                        var username_holder = "<span class='hide username-holder'>"+stranger['username']+"</span>";
                        var content = "<li class='list-group-item list-group-item-action'>\
                                        <div class='row'>\
                                            <div class='col-2 col-md-2'><img src='/static/media/images/maleuser.png' class='profile-pic'/></div>\
                                            <div class='col-md-10 col-10' style='cursor: pointer;'>\
                                                "+username_holder+"\
                                                <div class='name'><i class='fa fa-circle state offline'></i>&nbsp;<span>"+stranger['fullname']+"</span></div>\
                                            </div>\
                                        </div>\
                                    </li>"; 
                        $("#direct-msg-list").append(content);
                    }
                }
                if (show_notification){
                    show_notification = false;
                    $.each($("#direct-msg-list li"), function(index, value){
                        if ($(this).find(".username-holder").text() == author["username"]){                             

                            var content = "<div class='row justify-content-end'>\
                                        <div class='col-6 col-sm-7 col-md-7'>\
                                            <p class='sent-msg float-right'>\
                                                <strong>"+displayname+"</strong><span class='timestamp float-right'>"+ist_date+" &nbsp; "+est_date+"</span><br>\
                                                <span>"+message+"</span>\
                                                "+file_url+"\
                                            </p>\
                                        </div>\
                                        <div class='col-1 col-sm-1 col-md-1'>\
                                            <img src='/static/media/images/maleuser.png' class='chat-pic'/>&nbsp;\
                                        </div>\
                                    </div>";

                            if (author['username'] in unseen_messages)
                                unseen_messages[author["username"]].push(content);                             
                            else
                                unseen_messages[author["username"]] = [content];
                            
                            var target = $(this).find(".name").children(".notifier");                            
                            console.log($(target));
                            console.log(unseen_messages);
                            
                            if ($(target).length > 0)
                                $(target).text(unseen_messages[author["username"]].length);
                            else {
                                var notifier = "<span class='badge badge-primary notifier'>1</span>";
                                $(this).find(".name").append(notifier);
                            }    

                            return;
                        }
                    }); 
                } 
                if (loaded){
                    // update right chat panel messages
                    var messages = unseen_messages[selected_user];
                    $.each(messages, function(index, message){                
                        $("#messages").append(message);
                    });
                } 
                document.getElementById('messages').scrollTo(0, document.getElementById('messages').scrollHeight);
            };
        }
    });    

    // $(document).on("click", "#messages p", function(){
    //     //var user = $(this).children("strong").text();
    //     var user = $(this).children(".username-holder").text();
    //     var full_name = $(this).children("strong").text();
    //     localStorage.setItem("fullname", full_name);
    //     window.location.href = "/direct?user="+user;
    // });

    //send message with websocket
    function load_messages() {
        data = {
            "receiver": selected_user,
            "is_user": true
        };
        socket.send(JSON.stringify(data));                        
    }
    // show chat section and load user messages
    $(document).on("click", "#direct-msg-list li", function(){
        document.getElementById('chatPanel').removeAttribute('style');
        document.getElementById('divStart').setAttribute('style', 'display:none');
        hideChatList();

        $("#messages").empty();
        
        selected_user = $(this).find("span").eq(0).text();        
        
        var full_name = $(this).find("span").eq(1).text();
        var state = "offline";
        if ($(this).find(".state").hasClass("online"))
            state = "online";

        var classes = $(this).find(".state").attr("class");
        $("#chatPanel .under-name").find("i").removeClass();
        $("#chatPanel .under-name").find("i").addClass(classes);
        
        $("#chatPanel .name").find(".user-fullname").text(full_name);
        $("#chatPanel .name").find(".username-holder").text(selected_user);               
        $("#chatPanel .under-name").children("span").text(state);

        // load messages
        load_messages();

        // remove notifier and show messages
        var notifier = $(this).find(".notifier");
        if (notifier){
            $(notifier).remove();                              
        }                                
    });

    function send_message(){
        var msg = $("#text-message").val();
        console.log(msg);
        data = {
            "message": msg,        
            "receiver": selected_user
        };
        console.log(data);
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
                file = null;
            } else
                $("#err-msg").text("Only files less than 5MB allowed.");
        } else if (msg){
            console.log(JSON.stringify(data));
            socket.send(JSON.stringify(data));
        }    
        $("#text-message").val("");
    }

    // send message
    $("#msg-form").on("submit", function(e){
        e.preventDefault();
        send_message();
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

    $(document).on("click", "#rooms li", function(){
        var room = $(this).text();
        if (room)
            window.location.href = "/room?name="+room;
    });

    // onclick of online user
    // $(document).on("click", ".online-users a", function(){
    //     document.getElementById('chatPanel').removeAttribute('style');
    //     document.getElementById('divStart').setAttribute('style', 'display:none');
    //     hideChatList();
    //     $("#messages").empty();
        
    //     selected_user = $(this).find("span").eq(0).text();    
    //     var full_name = $(this).find("span").eq(1).text();        
    //     $("#chatPanel .name").text(full_name);

    //     // load messages
    //     load_messages();
    // });

    // logout the user
    $(document).on("click", "#linkSignOut", function(e){
        e.preventDefault();
        $.ajax({
            url: '/api/user',
            type: 'DELETE',
            success: function(response){
                window.location.href = "/"
            }
        });
    });
});  //closing of ready


//// FOR CREATE ROOM MEMBERS////
$(document).ready(function(){

    var multipleCancelButton = new Choices('#choices-multiple-remove-button', {
    removeItemButton: true,
    maxItemCount:5,
    searchResultLimit:100,
    renderChoiceLimit:100
    });
   
   
});

///////////////////////////
