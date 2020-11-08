// google login entrypoint
function start() {
    gapi.load('auth2', function(){
        auth2 = gapi.auth2.init({
            client_id: "973829616666-n71ceelkr8spfb1ldtt6318e54v1cebr.apps.googleusercontent.com"
        });
    });
}
// load script on page load
$(document).ready(function(){
    // callback to send authentication code to backend
    function signInCallback(authResult){
        if (authResult['code']) {
             $.ajax({
                type: 'POST',
                url: '/api/social_login',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                },
                contentType: "application/json",
                dataType: "json",
                data: JSON.stringify({"type": "google", "token": authResult['code']}),
                success: function(response){
                    var error = response["error"]
                    if (error){
                        $("#err").text(error);
                    } else
                        window.location.href="/"
                }
            });
        }
    }
    // attach callback on click of google login button
    $("#google-signin").on("click", function(){
        auth2.grantOfflineAccess().then(signInCallback);
    });
    // login to backend
    $("#login-form").on("submit", function(e){
        e.preventDefault();
        var form_data = {}
        $(this).find("input[name]").each(function (index, node) {
            form_data[node.name] = node.value;
        });
        $.post("/api/token", form_data, function(response){
            $("#err").text("");
            var error = response["error"]
            if (error)
                $("#err").text(error);
            else
                window.location.href = "/";
        });
    });
});