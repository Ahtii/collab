

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
    var selected_user = "";
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
               //$("#cur_user").text(user);
               $("#cur_user").text(name);
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
           socket = new WebSocket("ws://localhost:8000/api/user-connect");
           socket.onmessage = function(event) {
               var data = JSON.parse(event.data);
               var mid = data['id'];
               var sender = data['sender'];
               var receiver = data['receiver'];
               var author = data['author'];
               var message = data['message'];
               var ist_date = data['ist_date'];
               var est_date = data['est_date'];
               var room = data['room'];
               var file = data['file'];
               var file_url = "";
               var parent = $("#messages");               
               console.log(data["users"]);
               if(sender) {
                   var parent = $("#online-users ul");
                   parent.empty();
                   var receivers = data['users'];
                   $.each(receivers, function(index, receiver){
                       if (sender != receiver['username']){                           
                           var username_holder = "<span class='hide username-holder'>"+receiver['username']+"</span>";
                           var child = "<li>"+username_holder+"<a>"+receiver['fullname']+"</a></li>";
                           parent.append(child);
                       }
                   });
               }
               if (!room && (message || file)){
                   $("#no-message").addClass("hide");
                   $("#messages").removeClass("hide");
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
                       displayname = "you";
                       display_username = receiver['username'];
                       user_tag = receiver["fullname"];                       
                   }
                   var messages = $("#messages p");
                   var no_match = true;
                   $.each(messages, function(index, msg){
                       console.log(index);
                       var target_user = $(msg).children(".username-holder").text();
                       if (target_user == display_username){
                           $(msg).empty();
                           var notifier = "<i class='badge badge-primary notifier'>1</i>";
                           var content = "<span class='hide username-holder'>"+display_username+"</span><strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+ist_date+" &nbsp; "+est_date+"</span>"+notifier+"<br><span>"+displayname+"</span>: <span>"+message+"</span>"+file_url;
                           $(msg).addClass("highlight");
                           $(msg).append(content);
                           no_match = false;
                           return false;
                       }
                   });
                   if (no_match){
                       var username_holder = "<span class='hide username-holder'>"+display_username+"</span>";
                       var content = "<p>"+username_holder+"<strong>"+user_tag+"</strong> : &nbsp; <span class='date'>"+ist_date+" &nbsp; "+est_date+"</span><br><span>"+displayname+"</span>: <span>"+message+"</span>"+file_url+"</p>";
                       parent.append(content);
                   }
               }
            //    console.log(room);
            //    if (room){
            //        var room_name_html = "<li>"+room+"</li>";
            //        $("#rooms ul").append(room_name_html);
            //        console.log("inside add room code.");
            //    }
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
$(document).on("click", "#rooms li", function(){
    var room = $(this).text();
    if (room)
        window.location.href = "/room?name="+room;
});
// direct to personal chat
$(document).on("click", "#online-users ul li", function(){
    var user = $(this).children(".username-holder").text();
    // socket.close();
    var full_name = $(this).children("a").text();
    localStorage.setItem("fullname", full_name);
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
$(document).on("click", "#logout", function(){
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

