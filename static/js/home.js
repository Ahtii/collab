

/*Animation*/
const sign_in_btn = document.querySelector("#sign-in-btn");
const sign_up_btn = document.querySelector("#sign-up-btn");
const container = document.querySelector(".container");

sign_up_btn.addEventListener("click", () => {
  container.classList.add("sign-up-mode");
});

sign_in_btn.addEventListener("click", () => {
  container.classList.remove("sign-up-mode");
});


//var auth2;
// google login entrypoint
function start() {
  gapi.load('auth2', function(){
       auth2 = gapi.auth2.init({
          client_id: "973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com"
      });
  });
}

/* home jQuery */
$(document).ready(function(){
    var selected_user, file;
    var selected_room = "";
    var user = "", socket;
    var uid;    
    localStorage.removeItem("fullname");
    function genProfile(){

      $.get("/api/user", function(response){
        user = response["user"];   
        if (user){
           var name = response['full_name'];
           if ($("#auth").hasClass("hide")){
               $("#auth").removeClass("hide");
               $("#not-auth").addClass("hide");               
               $(".active-user").text(name);
           }
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
               var mid = data['id'];
               var sender = data['sender'];
               var receiver = data['receiver'];
               var author = data['author'];
               var message = data['message'];
               var ist_date = data['ist_date'];
               var est_date = data['est_date'];
               var last_message = data['last_message'];
               var room = data['room'];
               var file = data['file'];
               var file_url = "";               
               console.log(data);
               if (sender) {
                   var online_user_list = $(".online-users .dropdown-menu");
                   online_user_list.empty();
                   var receivers = data['users'];
                   $.each(receivers, function(index, receiver){
                       if (sender != receiver['username']){                           
                           var username_holder = "<span class='hide username-holder'>"+receiver['username']+"</span>";
                           //var child = "<li>"+username_holder+"<a>"+receiver['fullname']+"</a></li>";
                           var child = "<a class='dropdown-item'>"+username_holder+"<span>"+receiver['fullname']+"</span></a>"
                           online_user_list.append(child);
                       }
                   });                
               }
               if (!room && (message || file)){
                //    $("#no-message").addClass("hide");
                //    $("#messages").removeClass("hide");
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
                //    console.log(author["username"]);
                //    console.log(displayname);
                //    console.log(display_username);
                //    console.log(user_tag);                  

                //    var messages = $("#messages p");
                //    var no_match = true;
                //    $.each(messages, function(index, msg){
                //        console.log(index);
                //        var target_user = $(msg).children(".username-holder").text();
                //        if (target_user == display_username){
                //            $(msg).empty();
                //            var notifier = "<i class='badge badge-primary notifier'>1</i>";
                //            var content = "<span class='hide username-holder'>"+display_username+"</span><strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+ist_date+" &nbsp; "+est_date+"</span>"+notifier+"<br><span>"+displayname+"</span>: <span>"+message+"</span>"+file_url;
                //            $(msg).addClass("highlight");
                //            $(msg).append(content);
                //            no_match = false;
                //            return false;
                //        }
                //    });
                //    if (no_match){
                //        var username_holder = "<span class='hide username-holder'>"+display_username+"</span>";
                //        var content = "<p>"+username_holder+"<strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+ist_date+" &nbsp; "+est_date+"</span><br><span>"+displayname+"</span>: <span>"+message+"</span>"+file_url+"</p>";
                //        parent.append(content);
                //    }
                var username_holder = "<span class='hide username-holder'>"+display_username+"</span>";
                //var content = "<p>"+username_holder+"<strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+ist_date+" &nbsp; "+est_date+"</span><br><span>"+displayname+"</span>: <span>"+message+"</span>"+file_url+"</p>";
                //parent.append(content);
                if (last_message){
                    var content = "<li class='list-group-item list-group-item-action' onclick='StartChat()'>\
                                    <div class='row'>\
                                        <div class='col-2 col-md-2'><img src='/static/media/images/maleuser.png' class='profile-pic'/></div>\
                                        <div class='col-md-10 col-10' style='cursor: pointer;'>\
                                            "+username_holder+"\
                                            <div class='name'><span>"+user_tag+"</span></div>\
                                            <div class='under-name'> "+displayname+": &nbsp; "+message+"&nbsp;"+file_url+"</div>\
                                        </div>\
                                    </div>\
                                </li>"; 
                    $("#direct-msg-list").append(content);    
                } else {
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
                    }else {
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
                    $("#messages").append(content);            
                }                
               }
           };
        }
   });
  
    }  //brace of genProfile


  //code for registering user
  $("#register-form").on("submit",function(e){
      e.preventDefault();

      var form_data = {
        "first_name": $("#first_name").val(),
        "last_name": $("#last_name").val(),
        "email": $("#email").val(),
        "username": $("#username").val(),
        "password": $("#password").val()
      };
      console.log(form_data);
      $.post("/api/user", JSON.stringify(form_data),function(response){
        var error = response["error"];
        if (error)
          alert(error);
        else
          $("#sign-in-btn").trigger("click");
      });
  });

  // callback to send authentication code to backend
  function signInCallback(authResult){
    if (authResult['code']) {
         console.log("code is ");
         console.log(authResult['code']);
         $.ajax({
            type: 'POST',
            url: '/api/social-login',
            headers: {
                'X-Requested-With': 'XMLHttpRequest'
            },
            contentType: "application/json",
            dataType: "json",
            data: JSON.stringify({"type": "google", "token": authResult['code']}),
            success: function(response){
                var error = response["error"];
                if (error){
                    alert(error);
                } 
                else
                    genProfile();
            }
        });
    }
  }
  // attach callback on click of google login button
  $("#google-signin").on("click", function(){
    //e.preventDefault();
    auth2.grantOfflineAccess().then(signInCallback);
  });

  genProfile();

   // user login
   $("#login-form").on("submit", function(e){
    e.preventDefault();
    var form_data = {}
    $(this).find("input[name]").each(function (index, node) {
        form_data[node.name] = node.value;
        console.log(node.name);
        console.log(node.value);
    });
    $.post("/api/user/token", form_data, function(response){
        //$("#err").text("");
        var error = response["error"];
        if (error)
            alert(error);
        else{
          genProfile();
        } //brace of else

    });

}); //closing of login

$(document).on("click", "#messages p", function(){
    //var user = $(this).children("strong").text();
    var user = $(this).children(".username-holder").text();
    var full_name = $(this).children("strong").text();
    localStorage.setItem("fullname", full_name);
    window.location.href = "/direct?user="+user;
});
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

    selected_user = $(this).find("span").eq(0).text();    
    var full_name = $(this).find("span").eq(1).text();        
    $("#chatPanel .name").text(full_name);

    // load messages
    load_messages();
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
$(document).on("click", ".online-users a", function(){
    document.getElementById('chatPanel').removeAttribute('style');
    document.getElementById('divStart').setAttribute('style', 'display:none');
    hideChatList();

    selected_user = $(this).find("span").eq(0).text();    
    var full_name = $(this).find("span").eq(1).text();        
    $("#chatPanel .name").text(full_name);

    // load messages
    load_messages();
});
// direct to personal chat
$(document).on("click", "#online-users ul li", function(){
    var user = $(this).children(".username-holder").text();
    // socket.close();
    var full_name = $(this).children("a").text();
    localStorage.setItem("fullname", full_name);
    window.location.href = "/direct?user="+user;
});

// logout the user
$(document).on("click", "#linkSignOut", function(){
    $.ajax({
        url: '/api/user',
        type: 'DELETE',
        success: function(response){
            window.location.href = "/"
        }
    });
});

    // $.get("/api/user", function(response){
    //      user = response["user"];
    //      if (user){
    //         if ($("#auth").hasClass("hide")){
    //             $("#auth").removeClass("hide");
    //             $("#not-auth").addClass("hide");
    //             $("#cur_user").text(user);
    //         }
    //         $.get("/api/users/rooms", function(response){
    //             var rooms_list = response["rooms"]
    //             if (!jQuery.isEmptyObject(rooms_list)){
    //                 var parent = $("#rooms ul");
    //                 $.each(rooms_list, function(key, value){
    //                     child = "<li>"+value["name"]+"</li>";
    //                     parent.append(child);
    //                 });
    //             }
    //         });
    //         // create websocket
    //         socket = new WebSocket("ws://localhost:8000/api/user-connect");
    //         socket.onmessage = function(event) {
    //             var data = JSON.parse(event.data);
    //             var sender = data['sender'];
    //             var receiver = data['receiver'];
    //             var author = data['author'];
    //             var message = data['message'];
    //             var date = data['date'];
    //             var room = data['room'];
    //             var file = data['file'];
    //             var file_url = "";
    //             var parent = $("#messages");
    //             console.log(data);
    //             if(sender) {
    //                 var parent = $("#online-users ul");
    //                 parent.empty();
    //                 var receivers = data['receivers'];
    //                 $.each(receivers, function(index, receiver){
    //                     if (sender != receiver){
    //                         var child = "<li> <a>"+receiver+"</a></li>";
    //                         parent.append(child);
    //                     }
    //                 });
    //             }
    //             if (message || file){
    //                 $("#no-message").addClass("hide");
    //                 $("#messages").removeClass("hide");
    //                 if (file)
    //                     file_url = "<br><a href='"+file+"'>"+data['filename']+"</a>";
    //                 var user_tag = author;
    //                 if (user == author){
    //                     author = "you";
    //                     user_tag = receiver;
    //                 }
    //                 var messages = $("#messages p");
    //                 var no_match = true;
    //                 $.each(messages, function(index, msg){
    //                     console.log(index);
    //                     var user_msg = $(msg).children("strong").text();
    //                     if (user_msg == user_tag){
    //                         $(msg).empty();
    //                         var notifier = "<i class='badge badge-primary notifier'>1</i>";
    //                         var content = "<strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+date+"</span> &nbsp;"+notifier+"<br><span>"+author+"</span>: <span>"+message+"</span>"+file_url;
    //                         $(msg).addClass("highlight");
    //                         $(msg).append(content);
    //                         no_match = false;
    //                         return false;
    //                     }
    //                 });
    //                 if (no_match){
    //                     var content = "<p><strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+date+"</span><br><span>"+author+"</span>: <span>"+message+"</span>"+file_url+"</p>";
    //                     parent.append(content);
    //                 }
    //             }
    //         };
    //      }
    // });

    // $(document).on("click", "#messages p", function(){
    //     var user = $(this).children("strong").text();
    //     window.location.href = "/direct?user="+user;
    // });
    // $(document).on("click", "#rooms li", function(){
    //     var room = $(this).text();
    //     if (room)
    //        window.location.href = "/rooms?room="+room;
    // });
    // // change from public chat to personal chat
    // $(document).on("click", "#online-users ul a", function(){
    //    var user = $(this).text();
    //    socket.close();
    //    window.location.href = "/direct?user="+user;
    // });
    // //send message with websocket
    // function sendMessage() {
    //     var input = document.getElementById("messageText");
    //     data = {
    //         "message": input.value,
    //         "receiver": selected_user,
    //         "room": selected_room
    //     };
    //     socket.send(JSON.stringify(data));
    //     input.value = '';
    // }
    // // logout the user
    // $("#logout").on("click", function(){
    //     $.ajax({
    //         url: '/api/users',
    //         type: 'DELETE',
    //         success: function(response){
    //             window.location.href = "/"
    //         }
    //     });
    // });
});  //closing of ready









// //load script on page load
// $(document).ready(function(){

//   //code for registering user
//   $("#register-form").on("submit",function(e){
//       e.preventDefault();

//       var form_data = {
//         "first_name": $("#first_name").val(),
//         "last_name": $("#last_name").val(),
//         "email": $("#email").val(),
//         "username": $("#username").val(),
//         "password": $("#password").val()
//       };
//       console.log(form_data);
//       $.post("/api/users", JSON.stringify(form_data),function(response){
//         var error = response["error"];
//         if (error)
//           alert(error);
//         else
//           $("#sign-in-btn").trigger("click");
//       });
//   });

//   // callback to send authentication code to backend
//   function signInCallback(authResult){
//     if (authResult['code']) {
//          console.log("code is ");
//          console.log(authResult['code']);
//          $.ajax({
//             type: 'POST',
//             url: '/api/social_login',
//             headers: {
//                 'X-Requested-With': 'XMLHttpRequest'
//             },
//             contentType: "application/json",
//             dataType: "json",
//             data: JSON.stringify({"type": "google", "token": authResult['code']}),
//             success: function(response){
//                 var error = response["error"];
//                 if (error){
//                     alert(error);
//                 } 
//                 else
//                     alert("Gmail Login Successfull");
//             }
//         });
//     }
//   }
//   // attach callback on click of google login button
//   $("#google-signin").on("click", function(){
//     //e.preventDefault();
//     auth2.grantOfflineAccess().then(signInCallback);
//   });
//    // user login
//    $("#login-form").on("submit", function(e){
//     e.preventDefault();
//     var form_data = {}
//     $(this).find("input[name]").each(function (index, node) {
//         form_data[node.name] = node.value;
//         console.log(node.name);
//         console.log(node.value);
//     });
//     $.post("/api/users/token", form_data, function(response){
//         //$("#err").text("");
//         var error = response["error"];
//         if (error)
//             alert(error);
//         //else
//             //alert("Login Successfull");
//     });
// });

// }); //closing of ready

