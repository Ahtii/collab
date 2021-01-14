
//hiding welcome screen (opening chatbox on clicking user)
// function StartChat(){
//     document.getElementById('chatPanel').removeAttribute('style');
//     document.getElementById('divStart').setAttribute('style', 'display:none');
    
//     hideChatList();
// }


//show chat list on welcome screen
// function showChatList(){
//     document.getElementById('left-panel').classList.remove('d-none','d-md-block');
//     document.getElementById('right-panel').classList.add('d-none');
// }


// //hide chat list on welcome screen
// function hideChatList(){
//     document.getElementById('left-panel').classList.add('d-none','d-md-block');
//     document.getElementById('right-panel').classList.remove('d-none');
// }

// //for showing tooltips over Gsheet
// $(document).ready(function(){
//     $(".gsheet-tooltip").tooltip({
//         delay: {show: 0, hide: 250}
//     }); 
// });


//sending message on pressing Enter key
// function OnKeyDown(){
//     document.addEventListener('keydown', function(key){
//         if(key.which === 13){
//             SendMessage();
//         }
//     });
// }


//sending message
// function SendMessage(){
//     var message = ` <div class="row justify-content-end">
//                             <div class="col-6 col-sm-7 col-md-7">
//                                 <p class="sent-msg float-right">
//                                     ${document.getElementById('text-message').value}
//                                     <span class="timestamp float-right">11:11 am</span>
//                                 </p>
//                             </div>
//                             <div class="col-1 col-sm-1 col-md-1">
//                                 <img src="/static/media/images/maleuser.png" class="chat-pic" />
//                             </div>
//                     </div> `;

//     document.getElementById('messages').innerHTML += message;
//     document.getElementById('text-message').value = '';
//     document.getElementById('text-message').focus;

//     document.getElementById('messages').scrollTo(0, document.getElementById('messages').scrollHeight);
// }



// myProfile
// function myProfile(){
    
// }

//userProfile
// function userProfile(){

// }