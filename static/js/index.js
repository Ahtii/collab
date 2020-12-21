

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

/* home jQuery */
$(document).ready(function(){    
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
    // google login entrypoint
    start();
    function start() {
        gapi.load('auth2', function(){
            auth2 = gapi.auth2.init({
                client_id: "973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com"
            });
        });
    }

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
                    else{
                        //genProfile();
                        console.log("show profile");
                        window.location.reload()
                        //window.location.href = "/chat";
                    }    
                }
            });
        }
    }
    // attach callback on click of google login button
    $("#google-signin").on("click", function(){
        //e.preventDefault();
        auth2.grantOfflineAccess().then(signInCallback);
    });

    //genProfile();
    console.log("show profile");

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
          //genProfile();
          console.log("show profile");
         // window.location.href = "/chat";
         window.location.reload()
        } //brace of else

    });

    }); //closing of login
});  //closing of ready
