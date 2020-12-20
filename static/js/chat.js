
 //// FOR PROFILE PAGE /////////
    function edit_profile()
    {
        var myWindow;

        document.getElementById('probio').removeAttribute('disabled');
        document.getElementById('proname').removeAttribute('disabled');
        document.getElementById('prodesig').removeAttribute('disabled');
        document.getElementById('proimage').style.display="block";
        document.getElementById('prosave').style.display="block";
        document.getElementById('proname').style.border="thin solid black";
        document.getElementById('prodesig').style.border="thin solid black";
        document.getElementById('probio').style.border="thin solid";
        }
        var proName = document.getElementById("proname");
        proName.style.color = 'Crimson';
        proName.style.fontSize='medium';
        proName.style.fontWeight='bold';
        var prodesig = document.getElementById("prodesig");
        prodesig.style.color = 'seagreen';
        prodesig.style.fontSize='medium';
        prodesig.style.fontWeight='bold';
        var probio = document.getElementById("probio");
        probio.style.textAlign='center';
        

        function save()
        {
        //   event.target.getElementById= 'prosave';
        //   var proname = document.getElementById("proname");
        //   var save= document.getElementById("proname");
        //   var proname=save;
        console.log("testing");            
        }
        $("#profile-form").on("submit", function(e){
            e.preventDefault();
            var data = {
                "name": $("#proname").val(),
                "designation": $("#prodesig").val(),
                "bio": $("#probio").val()
            };
            console.log(data);
            $.post("/api/profile-save", JSON.stringify(data), function(response){
                console.log("working");
            });
    });
    // function closeWin()
    // {
    //    myWindow.close();
    // }


/* chat jQuery */
$(document).ready(function(){
    
    var selected_user, file;
    var selected_room, unseen_messages = [];
    var user = "", socket;
    var uid; 

    $.get("/api/user", function(response){
        user = response["user"];     
        if (user){
           var name = response['full_name'];
           $(".active-user").text(name);
           uid = response['id'];

            /* BISMA's CODE */

            $.get("/api/profile/"+uid, function(response){
                console.log(response);
            });

            /* BISMA's CODE END */

           $.get("/api/user/"+uid+"/room", function(response){
                var room_list = response["rooms"];
                console.log(room_list);
                if (!jQuery.isEmptyObject(room_list)){
                    //$("#roomMsg ul")
                    $.each(room_list, function(key, room){
                        var room_id_holder = "<span class='hide room-id-holder'>"+room["id"]+"</span>";
                        var room_layout = "<li class='list-group-item list-group-item-action'>\
                                            <div class='row'>\
                                                <div class='col-2 col-md-2'>\
                                                    <img src='/static/media/images/groups.png' class='profile-pic'/>\
                                                </div>\
                                                <div class='col-9 col-sm-8 col-md-8 col-lg-9' style='cursor: pointer;'>\
                                                    "+room_id_holder+"\
                                                    <div class='name'><span class='room-name'>"+room["name"]+"</span></div>\
                                                    <div class='under-name'>"+room["description"]+"</div>\
                                                </div>\
                                            </div>\
                                        </li>";
                        $("#room-msg-list").append(room_layout);
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
                            //console.log(panel_username);
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
                var show_direct_notification = false;
                var show_room_notification = false;
                //console.log(room);
                // code to show message
                if (message || file){  
                    if (file){
                        var full_path = file.split("/");
                        var file_owner = full_path[full_path.length - 3];
                        var file_name = full_path[full_path.length - 1];    
                        file_url = "<br><a href='/preview-file?user="+file_owner+"&file="+file_name+"'>"+data['filename']+"</a>";
                    }                                          
                    var displayname = author["fullname"];
                    var user_tag = displayname;
                    var display_username = author['username']; 
                    if (receiver){
                        if (user == display_username){   
                            displayname = "You";
                            display_username = receiver['username'];
                            user_tag = receiver["fullname"];                       
                        }  
                        console.log(data);    
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
                            console.log(panel_selected_user);
                            console.log(room);
                            var content;
                            // decide position of message box
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
                                show_direct_notification = true;                              
                            }       
                            if (content)
                                $("#messages").append(content);            
                        }    
                    } else if (room) {
                        if (user == display_username){   
                            displayname = "You";
                        } 
                        console.log(data);    
                        var username_holder = "<span class='hide username-holder'>"+display_username+"</span>";                                                
                        var panel_selected_user = $("#chatPanel .name").find(".user-fullname").text();
                        console.log(panel_selected_user);
                        console.log(room);
                        var content;
                        // decide position of message box                                                       
                        if (panel_selected_user == room){
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
                            } else {
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
                            }    
                        } else {
                            show_room_notification = true;   
                            console.log("show room notification");                           
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
                                                <!--<div class='name mt-2'>\
                                                    <i class='fa fa-circle state offline'></i>&nbsp;<span>"+user_tag+"</span>\
                                                </div>\
                                                <div class='under-name'> \
                                                    "+displayname+": &nbsp; "+message+"&nbsp;"+file_url+"\
                                                </div>-->\
                                                <div class='name'><i class='fa fa-circle state offline'></i>&nbsp;<span>"+stranger['fullname']+"</span></div>\
                                            </div>\
                                        </div>\
                                    </li>"; 
                        $("#direct-msg-list").append(content);
                    }
                }
                if (show_direct_notification){
                    show_direct_notification = false;
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
                            //console.log($(target));
                            //console.log(unseen_messages);
                            
                            if ($(target).length > 0)
                                $(target).text(unseen_messages[author["username"]].length);
                            else {
                                var notifier = "<span class='badge badge-primary notifier'>1</span>";
                                $(this).find(".name").append(notifier);
                            }    

                            return;
                        }
                    }); 
                }else if (show_room_notification){
                    show_room_notification = false; 
                    console.log("setup room notification"); 
                    $.each($("#room-msg-list li"), function(index, value){
                        console.log("inside room list");
                        console.log($(this).find(".room-name").text());
                        console.log(room);
                        if ($(this).find(".room-name").text() == room){                             
                            console.log("found room match");
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

                            if (room in unseen_messages)
                                unseen_messages[room].push(content);                             
                            else
                                unseen_messages[room] = [content];
                            
                            var target = $(this).find(".name").children(".notifier");                            
                            console.log($(target));
                            console.log(unseen_messages);
                            
                            if ($(target).length > 0)
                                $(target).text(unseen_messages[room].length);
                            else {
                                var notifier = "<span class='badge badge-primary notifier'>1</span>";
                                $(this).find(".name").append(notifier);
                                console.log($(target));
                                console.log(unseen_messages);
                            }    
                            return;
                        }
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
        console.log("load message");        
        data = {            
            "is_user": true
        };
        if (selected_user)
            data['receiver'] = selected_user;
        else if (selected_room)    
            data['room'] = selected_room;
        console.log(data);
        socket.send(JSON.stringify(data));                        
    }

    // show chat section and load user messages
    $(document).on("click", "#direct-msg-list li", function(){
        document.getElementById('chatPanel').removeAttribute('style');
        document.getElementById('divStart').setAttribute('style', 'display:none');
        hideChatList();

        $("#messages").empty();
        selected_room = "";

        $(".panel-pic").attr("src", "/static/media/images/maleuser.png");        
        
        selected_user = $(this).find("span").eq(0).text();        
        
        var full_name = $(this).find("span").eq(1).text();
        var state = "offline";
        if ($(this).find(".state").hasClass("online"))
            state = "online";

        if ($("#chatPanel .under-name").hasClass("hide"))
            $("#chatPanel .under-name").removeClass("hide");

        var classes = $(this).find(".state").attr("class");
        $("#chatPanel .under-name").find("i").removeClass();
        $("#chatPanel .under-name").find("i").addClass(classes);
        
        $("#chatPanel .name").find(".user-fullname").text(full_name);
        $("#chatPanel .name").find(".username-holder").text(selected_user);               
        $("#chatPanel .under-name").children("span").text(state);

        // load messages
        load_messages();
        //$.get("/api/user/"+uid+"/messages");

        // remove notifier and show messages
        var notifier = $(this).find(".notifier");
        if (notifier){
            $(notifier).remove();                              
        }  
        
        var index = unseen_messages.indexOf(selected_user);
        unseen_messages.splice(index, 1);
    });

    function send_message(){
        var msg = $("#text-message").val();
        console.log(msg);
        data = {
            "message": msg,        
            "receiver": selected_user,
            "room": selected_room
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

    // $(document).on("click", "#rooms li", function(){
    //     var room = $(this).text();
    //     if (room)
    //         window.location.href = "/room?name="+room;
    // });

    /* ROOM CODE */

    $(".tab-header .nav-item").on("click", function(){
        var tab = $(this).find("a").attr("id");        
        // if (tab == "tab-room-message"){

        // }else{

        // }
    });

    $(document).on("click", "#room-msg-list li", function(){
        document.getElementById('chatPanel').removeAttribute('style');
        document.getElementById('divStart').setAttribute('style', 'display:none');
        hideChatList();

        $("#messages").empty();  
        selected_user = "";      
        $(".panel-pic").attr("src", "/static/media/images/groups.png");                

        room_id = $(this).find(".room-id-holder").text();
        selected_room = $(this).find(".room-name").text();
        
        console.log(room_id);
        console.log(selected_room);       

        // var full_name = $(this).find("span").eq(1).text();
        // var state = "offline";
        // if ($(this).find(".state").hasClass("online"))
        //     state = "online";

        // var classes = $(this).find(".state").attr("class");
        // $("#chatPanel .under-name").find("i").removeClass();
        // $("#chatPanel .under-name").find("i").addClass(classes);
        
        $("#chatPanel .name").find(".user-fullname").text(selected_room);
        $("#chatPanel .name").find(".username-holder").text(room_id);               
        $("#chatPanel .under-name").addClass("hide");

        // console.log("before load of messages");
        // console.log($("#messages"));

         // load messages
         load_messages();

        // console.log("after load of messages");
        // console.log($("#messages"));

        // remove notifier and show messages
        var notifier = $(this).find(".notifier");
        if (notifier){
            $(notifier).remove();                              
        }         
        
        // var index = unseen_messages.indexOf(selected_room);
        // unseen_messages.splice(index, 1);
    });
    
    // on click of create room
    $("#roomButton").on("click", function(){
        $("#user-list").empty();
        $.get("/api/users", function(response){
            var participants = response["users"];
            $.each(participants, function(index, participant){ 
                if (participant['username'] != user){               
                    var participant_layout = "<li class='list-group-item' style='text-align: left;'>\
                                            <span class='hide username-holder'>"+participant["username"]+"</span>\
                                            <input type='checkbox'>&nbsp;\
                                            <span class='user-fullname'>"+participant["fullname"]+"</span>\
                                    </li>";
                    $("#user-list").append(participant_layout);
                }    
            });
        });
        // $("#userList").empty;
        // console.log($("#userList"));
        // $.get("/api/users", function(response){
        //     var participants = response["users"];
        //     $.each(participants, function(index, participant){ 
        //         if (participant['username'] != user){  
        //             console.log(participant["fullname"]); 
        //             // $('#userList').append($('<option/>', { 
        //             //     value: participant['username'],
        //             //     text : participant['fullname'] 
        //             // }));            
        //             var participant_layout = "<option value="+participant["username"]+">"+participant["fullname"]+"</option>";
        //             console.log(participant_layout);
        //             $("#userList").append(participant_layout);
        //         }
        //     });
        // });
    });

    $(document).on("submit", "#room-form", function(e){
        e.preventDefault();        
        var selected_participants = [];
        $.each($("#user-list li"), function(index, user){
            var checked = $(user).find("input").is(":checked");
            if (checked)
                selected_participants.push($(user).find(".username-holder").text());
        }); 
        var data = {
            "name": $("#roomName").val(),
            "description": $("#roomDesc").val(),
            "participants": selected_participants
        }
        $.post("/api/user/"+uid+"/room", JSON.stringify(data), function(response){
            var error = response["error"];
            if (error){
                $("#err").text(error);
            } else
                $("#createRoom").modal("toggle");
        });
        // var room = $(this).text();
        // if (room)
        //     window.location.href = "/room?name="+room;
    });

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
    
    ///////////////////////////
  
///////////////////////////

   

    ////////////////////////////////////////////////
});  //closing of ready
