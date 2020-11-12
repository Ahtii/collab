
$(document).ready(function(){
    // get current user
    $.get("/api/user", function(response){
         var current_user = response["user"]
         if (current_user){
            // get all users
            $.get("/api/users", function(response){
                var users_list = response["users"]
                if (!jQuery.isEmptyObject(users_list)){
                    var parent = $("#participants ul");
                    $.each(users_list, function(key, value){
                        if (current_user != value){
                            child = "<li> <a>"+value+"</a> </li>";
                            parent.append(child);
                        }
                    });
                }
            });
         }
    });
    sel_participants = [];
    // collected selected participants
    $(document).on("click", "#participants li", function(){
        var parent = $("#sel-participants ul");
        var selected_participant = $(this).text();
        var found = false;
        var target = $("#sel-participants li");
        $.each(target, function(idx, ele){
            if (selected_participant == $(ele).text()){
                found = true;
                return false;
            }
        });
        if (!found){
            html = "<li>"+selected_participant+"</li>"
            $(parent).append(html);
            sel_participants.push(selected_participant);
        }
    });
    // create room
    $("#room-form").on("submit", function(e){
        e.preventDefault();
        data = {
            "name": $("#room-name").val(),
            "description": $("#room-desc").val(),
            "participants": sel_participants
        };
        console.log(data);
        $.post("/api/users/rooms",JSON.stringify(data), function(response){
            var error = response["error"];
            if (error){
                $("#err").text(error);
            } else {
                window.location.href = "/"
            }
        });
    });
});