

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

////////////// For Validation ////////////////////

 ////////////////// FOR PASSWORD //////////////////

//  var myInput = document.getElementById("password");
//  var letter = document.getElementById("letter");
//  var capital = document.getElementById("capital");
//  var number = document.getElementById("number");

//  myInput.onkeyup = function() {
//     var lowerCaseLetters = /[a-z]/g;
//     if (myInput.value.match(lowerCaseLetters)) {
//        letter.classList.remove("wrong");
//        letter.classList.add("correct");
//     } else {
//        letter.classList.remove("correct");
//        letter.classList.add("wrong");
//     }
//     var upperCaseLetters = /[A-Z]/g;
//     if (myInput.value.match(upperCaseLetters)) {
//        capital.classList.remove("wrong");
//        capital.classList.add("correct");
//     } else {
//        capital.classList.remove("correct");
//        capital.classList.add("wrong");
//     }
//     var numbers = /[0-9]/g;
//     if (myInput.value.match(numbers)) {
//        number.classList.remove("wrong");
//        number.classList.add("correct");
//     } else {
//        number.classList.remove("correct");
//        number.classList.add("wrong");
//     }
//     if(myInput.value.length >= 8) {
//         length.classList.remove("invalid");
//         length.classList.add("valid");
//       } else {
//         length.classList.remove("valid");
//         length.classList.add("invalid");
//       }
// };
///////////////////////////////////////////


var isfError = false;
var isuError = false;
var iseError = false;
var ispError = false;


////////////// FOR FIRST NAME ///////////////

function fnameFunc(){

    var fnamepattern = /^[A-Za-z]{3,15}$/;

    var f = document.getElementById("first_name").value;

    if(f==""){
        document.getElementById("fmessage").innerHTML = "Name can't be empty. ";
        isfError = true;
        return false;
    }
    if(f.indexOf(' ') >= 0){
        document.getElementById("fmessage").innerHTML = "Name can't have spaces. ";
        isfError = true;
        return false;
    }
    if(f.length<3){
        document.getElementById("fmessage").innerHTML = "Name can't be less than 3 characters. ";
        isfError = true;
        return false;
    }
    if(f.length>15){
        document.getElementById("fmessage").innerHTML = "Name can't be more than 15 characters. ";
        isfError = true;
        return false;
    }
    if(f.match(fnamepattern)){
        document.getElementById("fmessage").innerHTML = "Valid. ";
        // document.getElementById("submit").removeAttribute('disabled');
        isfError = false;
        true;}
        else {
            document.getElementById("fmessage").innerHTML = "Symbols and numbers are not allowed. ";
            isfError = true;
            return false;
        }

} //nameFunc close

///////////////// FOR USERNAME /////////////////////

function unameFunc(){
    var usernamepattern = /^[A-Za-z0-9]{3,10}$/;

    var u = document.getElementById("username").value;

    if(u==""){
        document.getElementById("umessage").innerHTML = "Username can't be empty. ";
        isuError = true;
        return false;
    }
    if(u.indexOf(' ') >= 0){
        document.getElementById("umessage").innerHTML = "Username can't have spaces. ";
        isuError = true;
        return false;
    }
    if(u.length<3){
        document.getElementById("umessage").innerHTML = "Username can't be less than 3 characters. ";
        isuError = true;
        return false;
    }
    if(u.length>10){
        document.getElementById("umessage").innerHTML = "Username can't be more than 10 characters. ";
        isuError = true;
        return false;
    }
    if(u.match(usernamepattern)){
        document.getElementById("umessage").innerHTML = "Valid. ";
        // document.getElementById("submit").removeAttribute('disabled');
        isuError = false;
        true;}
        else {
            document.getElementById("umessage").innerHTML = "Symbols are not allowed. ";
            isuError = true;
            return false;
        }
} //unameFunc close

///////////////// FOR EMAIL /////////////////////////

function emailFunc(){
    var emailpattern = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}$/;

    var e = document.getElementById("email").value;

    if(e==""){
        document.getElementById("emessage").innerHTML = "Email can't be empty. ";
        iseError = true;
        return false;
    }
    if(e.indexOf(' ') >= 0){
        document.getElementById("emessage").innerHTML = "Email can't have spaces. ";
        iseError = true;
        return false;
    }
    // if(e.length<3){
    //     document.getElementById("emessage").innerHTML = "Email can't be less than 3 characters. ";
    //     iseError = true;
    //     return false;
    // }
    // if(e.length>10){
    //     document.getElementById("emessage").innerHTML = "Email can't be more than 10 characters. ";
    //     iseError = true;
    //     return false;
    // }
    if(e.match(emailpattern)){
        document.getElementById("emessage").innerHTML = "Valid. ";
        // document.getElementById("submit").removeAttribute('disabled');
        iseError = false;
        true;}
        else {
            document.getElementById("emessage").innerHTML = "";
            iseError = true;
            return false;
        }
} //emailFunc close

/////////////////// FOR PASSWORD ///////////////////

function passFunc(){
    var passpattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

    var p = document.getElementById("password").value;
    var uu = document.getElementById("username").value;

    if(p==""){
        document.getElementById("pmessage").innerHTML = "Password can't be empty. ";
        ispError = true;
        return false;
    }
    if(p.length<8){
        document.getElementById("pmessage").innerHTML = "Password can't be less than 8 characters. ";
        ispError = true;
        return false;
    }
    if(p.indexOf(' ') >= 0){
        document.getElementById("pmessage").innerHTML = "Password can't have spaces. ";
        ispError = true;
        return false;
    }
    if(p == uu){
        document.getElementById("pmessage").innerHTML = "Password can't be same as username. ";
        ispError = true;
        return false;
    }
   
    if(p.match(passpattern)){
        document.getElementById("pmessage").innerHTML = "Valid. ";
        // document.getElementById("submit").removeAttribute('disabled');
        ispError = false;
        true;}
        else {
            document.getElementById("pmessage").innerHTML = "Password must contain lowercase, uppercase and a number. ";
            ispError = true;
            return false;
        }
} //passFunc close

/////////////// FOR CONFIRM PASSWORD ///////////////

function cpassFunc(){
    // var cpasspattern = /^(?=.*\d)(?=.*[a-z])(?=.*[A-Z]).{8,}$/;

    var cp = document.getElementById("cpassword").value;
    var pp = document.getElementById("password").value;

    if(cp==""){
        document.getElementById("cpmessage").innerHTML = "Password didn't match. ";
        iscpError = true;
        return false;
    }
    if(cp.indexOf(' ') >= 0){
        document.getElementById("cpmessage").innerHTML = "Password didn't match. ";
        iscpError = true;
        return false;
    }
    if(cp.match(pp)){
        document.getElementById("cpmessage").innerHTML = "Password matched ";
        // document.getElementById("submit").removeAttribute('disabled');
        iscpError = false;
        true;}
        else {
            document.getElementById("cpmessage").innerHTML = "Password didn't match.";
            iscpError = true;
            return false;
        }
} //cpassFunc close
///////////////////////////////////////////////////


$(document).ready(function(){    
    //code for registering user
    $("#register-form").on("submit",function(e){
        e.preventDefault();

        // var form_data = {
        //     "first_name": $("#first_name").val(),
        //     "last_name": $("#last_name").val(),
        //     "email": $("#email").val(),
        //     "username": $("#username").val(),
        //     "password": $("#password").val()
        // };
        var form_data = {
            "full_name": $("#full_name").val(),
            "email": $("#email").val(),
            "password": $("#password").val()
        };        
        console.log(form_data);
        console.log(isfError);
        console.log(iseError);
        console.log(isuError);
        console.log(ispError);
        console.log(iscpError);
        //if(isfError == false && isuError == false && iseError == false && ispError == false && iscpError == false){
            $.post("/api/user", JSON.stringify(form_data),function(response){
                var error = response["error"];
                if (error)
                    alert(error);
                else
                    $("#sign-in-btn").trigger("click");
            });
        //}        
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


// Disable form submissions if there are invalid fields
(function() {
    'use strict';
    window.addEventListener('load', function() {
    // Get the forms we want to add validation styles to
    var forms = document.getElementsByClassName('needs-validation');
    // Loop over them and prevent submission
    var validation = Array.prototype.filter.call(forms, function(form) {
    form.addEventListener('submit', function(event) {
        if (form.checkValidity() === false) {
            event.preventDefault();
            event.stopPropagation();
    }
    form.classList.add('was-validated');
    }, false);
    });
    }, false);
 })();


 