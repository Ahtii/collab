// load script on page load
$(document).ready(function(){
    // send data to backend on submit
    $("#register-form").on("submit", function(e){
        e.preventDefault();
        var form_data = {
            "first_name": $("#firstname").val(),
            "last_name": $("#lastname").val(),
            "email": $("#email").val(),
            "username": $("#username").val(),
            "password": $("#password").val(),
        };
        $.post("/api/users", JSON.stringify(form_data), function(response){
            $("#err").text("");
            var error = response["error"]
            if (error)
                $("#err").text(error);
            else
                window.location.href = "/login";
        });
    });
});