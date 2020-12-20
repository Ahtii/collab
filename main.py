from sqlalchemy.orm import Session
import database, os, pathlib
from users import validators, views, models
from users.views import OAuth2PasswordBearerWithCookie
from fastapi import FastAPI, Depends, Response, Request, Form, UploadFile, File
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.templating import Jinja2Templates
from fastapi import WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from typing import List
from starlette.responses import FileResponse
from fastapi.responses import StreamingResponse
import random, magic

# Create the database tables
#models.Base.metadata.create_all(bind=engine)


app = FastAPI()
# authentication
TOKEN_MANAGER = OAuth2PasswordBearerWithCookie(tokenUrl="/api/users/token")
# websockets
socket_manager = views.SocketManager()
# static files
app.mount("/static", StaticFiles(directory="static"), name="static")

FILE_SIZE = 5000000

# create request session
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

templates = Jinja2Templates(directory="templates")


# TEMPLATES

# index template
@app.get("/")
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# chat template
@app.get("/chat",  include_in_schema=False)
def chat(request: Request):    
    return templates.TemplateResponse("chat.html", {"request": request})

# render file template
@app.get("/preview-file/", include_in_schema=False)
def preview_file(request: Request):    
    user = str(request.query_params['user'])
    filename = str(request.query_params['file'])  
    absolute_path = views.gen_file_dir(user, __file__) + "/" + filename    
    mime = magic.Magic(mime=True)
    mtype = mime.from_file(absolute_path)
    if "image" in mtype or "pdf" in mtype:
        return FileResponse(absolute_path, media_type=mtype)    
    else:
        return FileResponse(absolute_path, filename=filename)            
    # file = open(absolute_path, mode="rb")
    # return StreamingResponse(file, media_type=mtype)


# direct chat template
@app.get("/direct", include_in_schema=False)
def direct(request: Request):
    return templates.TemplateResponse("direct.html", {"request": request})

# room chat template
@app.get("/room", include_in_schema=False)
def room(request: Request):
    return templates.TemplateResponse("room.html", {"request": request})

# room template
# @app.get("/create_room", include_in_schema=False)
# def create_room(request: Request):
#     return templates.TemplateResponse("create_room.html", {"request": request})

    # API ENDPOINTS


@app.get("/api/user")
def get_current_user(request: Request, db: Session = Depends(get_db)):
    response = {}
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:        
        response = {
            "full_name": views.get_fullname(user),
            "user": user.username,
            "id": user.id
        }
    return response


# get all users
@app.get("/api/users")
def get_all_users(db: Session = Depends(get_db)):
    return views.get_all_users(db)


# create a user
@app.post("/api/user")
async def create_user(user: validators.RegisterValidator, db: Session = Depends(get_db)):
    response = views.register(db, user)
    if response['user']:
        await socket_manager.get_stranger(response['user'])
        response = {}
    return response    


# login the user and generate token for further authentication
@app.post("/api/user/token")
async def authenticate(credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = views.authenticate(db, credentials.username, credentials.password)
    response = {"error": "Incorrect username or password"}
    if user:
        response = Response()
        access_token = views.gen_token(user.username)
        response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return response


# logout the user
@app.delete("/api/user")
async def logout(request: Request, response: Response, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        await socket_manager.delete(user)        
        response.delete_cookie("access_token")           
    return user


# authenticating socail login and generating token
@app.post("/api/social-login", include_in_schema=False)
async def social_login(request: Request, response: Response, data: validators.SocialLoginValidator,
                 db: Session = Depends(get_db)):
    response = views.social_login(db, request, response, data)
    if response['user']:
        await socket_manager.get_stranger(response['user'])
        response = {}
    return response    



def get_old_conversation(id):
    return "WITH cte AS (\
              SELECT *, ROW_NUMBER() OVER (PARTITION BY LEAST(sender_id, receiver_id),\
                                GREATEST(sender_id, receiver_id)\
                                ORDER BY created_date DESC) rn\
              FROM personal_message\
              WHERE sender_id = "+id+" OR receiver_id = "+id+"\
        )\
        SELECT id, sender_id, text, created_date, receiver_id, attachment_url\
        FROM cte\
        WHERE rn = 1;"


# for chat
@app.websocket("/chat")
async def connect_user(websocket: views.WebSocket, db: Session = Depends(get_db)):
    # setup code for each connection
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:        
        await socket_manager.connect(websocket, user)        
        await socket_manager.get_online_users()
        users = db.query(models.User).all()        
        messages = db.execute(get_old_conversation(str(user.id)))
        friends = []
        for message in messages:
            sender = db.query(models.User).filter(
                models.User.id == message.sender_id
            ).first()
            receiver = db.query(models.User).filter(
                models.User.id == message.receiver_id
            ).first()
            msg_data = {
                "id": message.id,                 
                "author": {
                    "username": sender.username,
                    "fullname": views.get_fullname(sender)
                },
                "message": message.text,
                "ist_date": views.get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                "est_date": views.get_timezone(message.created_date, "US/Eastern")  + " EST",                                
                "receiver": {
                    "username": receiver.username,
                    "fullname": views.get_fullname(receiver),
                },                
                "last_message": True,
                "user": user.username
            }
            if sender.id != user.id:
                friends.append(sender)                
            else:
                friends.append(receiver)    
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            await socket_manager.populate_old_messages(msg_data)            
        #users = db.query(models.User).all()            
        #await socket_manager.get_registered_users(users, friends, user)
        strangers = list((set(users) - set(friends)) - set([user]))     
        for stranger in strangers:                                  
            await socket_manager.get_stranger(stranger)
        response = views.get_rooms(user, db)
        rooms = response["rooms"]
        if rooms:
            await socket_manager.populate_rooms(rooms, user)
        await socket_manager.get_online_users()
        try:
            while True:
                data = await websocket.receive_json()
                receiver = data.get('receiver')
                room = data.get('room')                                                      
                if data.get('is_user'):                                  
                    db = database.SessionLocal()                                                           
                    if receiver:                        
                        receiver = db.query(models.User).filter(
                            models.User.username == receiver
                        ).first()
                        #print(db.query(models.PersonalMessage).all())
                        old_messages = db.query(models.PersonalMessage).filter(
                            ((models.PersonalMessage.sender_id == user.id) &
                            (models.PersonalMessage.receiver_id == receiver.id)) |
                            ((models.PersonalMessage.sender_id == receiver.id) &
                            (models.PersonalMessage.receiver_id == user.id))
                        ).order_by(models.PersonalMessage.created_date).all()
                        #old_messages = db.execute("select * from personal_message where sender_id = "+str(user.id)+" and receiver_id = "+str(receiver.id)+" or sender_id = "+str(receiver.id)+" and receiver_id = "+str(user.id)+";")
                        for message in old_messages:
                            # if message.sender_id == user.id:
                            #     sender = user
                            #     receiver = receiver
                            # else:
                            #     sender = receiver
                            #     receiver = user
                            sender = db.query(models.User).filter(
                                models.User.id == message.sender_id
                            ).first()
                            receiver = db.query(models.User).filter(
                                models.User.id == message.receiver_id
                            ).first()
                            msg_data = {
                                "id": message.id,
                                "author": {
                                    "username": sender.username,
                                    "fullname": views.get_fullname(sender)
                                },
                                "message": message.text,
                                "ist_date": views.get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                                "est_date": views.get_timezone(message.created_date, "US/Eastern")  + " EST",
                                "receiver": {
                                    "username": receiver.username,
                                    "fullname": views.get_fullname(receiver)
                                },
                                "user": user.username
                            }
                            if message.attachment_url:
                                filename = message.attachment_url.split("/")[-1]
                                msg_data.update({
                                    "file": str(message.attachment_url),
                                    "filename": filename
                                })
                            print("message sender is: ")
                            print(sender.username) 
                            print("message receiver is: ")
                            print(receiver.username)
                            print("message text is: ")
                            print(message.text)
                            await socket_manager.populate_old_messages(msg_data)                    
                    else:
                        room = db.query(models.Room).filter(models.Room.name == room).first()
                        RoomMessage = models.RoomMessage
                        old_messages = db.query(RoomMessage).filter(
                            RoomMessage.room_id == room.id
                        ).order_by(RoomMessage.created_date).all()
                        for message in old_messages:
                            if message.sender_id == user.id:
                                sender = user
                            else:
                                sender = db.query(models.User).filter(
                                    models.User.id == message.sender_id
                                ).first()
                                sender = sender
                            msg_data = {
                                "id": message.id,
                                "author": {
                                    "username": sender.username,
                                    "fullname": views.get_fullname(sender)
                                },
                                "message": message.text,
                                "ist_date": views.get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                                "est_date": views.get_timezone(message.created_date, "US/Eastern")  + " EST",               
                                "room": room.name,
                                "user": user.username
                            }
                            if message.attachment_url:
                                filename = message.attachment_url.split("/")[-1]
                                msg_data.update({
                                    "file": str(message.attachment_url),
                                    "filename": filename
                                })
                            await socket_manager.populate_old_messages(msg_data)
                else:
                    if receiver:                              
                        #data.update({"sender_id": user.id, "username": user.username})
                        data.update({"user": user})
                        file_data = data.get('file')
                        if file_data:
                            file_size = file_data['size']
                            if file_size <= FILE_SIZE:                        
                                try:                    
                                    file = await websocket.receive_bytes()
                                    filename = file_data['filename']
                                    file_dir = views.gen_file_dir(user.username, __file__)
                                    file_url = views.create_file(file_dir, filename, file)
                                    data.update({
                                        "file": file_url,
                                        "filename": filename
                                    })  
                                except Exception as e:
                                    print("error: ")
                                    print(e) 
                            else:                        
                                print("file size exceeded!")
                        message = views.create_message(db, data)
                        await socket_manager.to_specific_user(message)                                                          
                    else:
                        file_data = data.get('file')
                        if file_data:
                            file_size = file_data['size']
                            if file_size <= FILE_SIZE:
                                file = await websocket.receive_bytes()
                                filename = file_data['filename']
                                file_dir = views.gen_file_dir(room.name, __file__)
                                file_url = views.create_file(file_dir, filename, file)
                                data.update({
                                    "file": file_url,
                                    "filename": filename
                                })
                        data['user'] = user.username        
                        message = views.create_room_message(db, data)
                        await socket_manager.to_room_participants(message)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)                        


# for profile
'''@app.websocket("/api/user-connect")
async def connect_user(websocket: views.WebSocket, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:        
        await socket_manager.connect(websocket, user)
        await socket_manager.get_online_users()
        messages = db.execute(get_old_conversation(str(user.id)))
        for message in messages:
            sender = db.query(models.User).filter(
                models.User.id == message.sender_id
            ).first()
            receiver = db.query(models.User).filter(
                models.User.id == message.receiver_id
            ).first()
            msg_data = {
                "id": message.id, 
                # "author": sender.username,
                "author": {
                    "username": sender.username,
                    "fullname": views.get_fullname(sender)
                },
                "message": message.text,
                "ist_date": views.get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                "est_date": views.get_timezone(message.created_date, "US/Eastern")  + " EST",                
                # "receiver": receiver.username,
                "receiver": {
                    "username": receiver.username,
                    "fullname": views.get_fullname(receiver),
                },
                "user": user.username
            }
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            await socket_manager.populate_old_messages(msg_data)
        response = views.get_rooms(user, db)
        rooms = response["rooms"]
        if rooms:
            await socket_manager.populate_rooms(rooms, user)
        try:
            while True:
                await websocket.receive_json()
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)'''        

# for direct chat
@app.websocket("/api/user-chat/{receiver}")
async def direct_chat(websocket: views.WebSocket, receiver: str, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)        
        print("receiver")
        print(receiver)
        receiver = db.query(models.User).filter(models.User.username == receiver).first()
        old_messages = db.query(models.PersonalMessage).filter(
            ((models.PersonalMessage.sender_id == user.id) &
             (models.PersonalMessage.receiver_id == receiver.id)) |
            ((models.PersonalMessage.sender_id == receiver.id) &
             (models.PersonalMessage.receiver_id == user.id))
        ).order_by(models.PersonalMessage.created_date).all()
        for message in old_messages:
            if message.sender_id == user.id:
                sender = user
                receiver = receiver
            else:
                sender = receiver
                receiver = user
            msg_data = {
                "id": message.id,
                "author": {
                    "username": sender.username,
                    "fullname": views.get_fullname(sender)
                },
                "message": message.text,
                "ist_date": views.get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                "est_date": views.get_timezone(message.created_date, "US/Eastern")  + " EST",
                "receiver": {
                    "username": receiver.username,
                    "fullname": views.get_fullname(receiver)
                },                
                "user": user.username
            }
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            # await socket_manager.specific(data)
            await socket_manager.populate_old_messages(msg_data)
        try:
            print("file is")
            print("testing")
            while True:
                data = await websocket.receive_json()   
                receiver = data["receiver"]                                
                #data.update({"sender_id": user.id, "username": user.username})
                data.update({"user": user})
                file_data = data.get('file')
                if file_data:
                    file_size = file_data['size']
                    if file_size <= FILE_SIZE:                        
                        try:                    
                            file = await websocket.receive_bytes()
                            filename = file_data['filename']
                            file_dir = views.gen_file_dir(user.username, __file__)
                            file_url = views.create_file(file_dir, filename, file)
                            data.update({
                                "file": file_url,
                                "filename": filename
                            })  
                        except Exception as e:
                            print("error: ")
                            print(e) 
                    else:                        
                        print("file size exceeded!")
                message = views.create_message(db, data)
                await socket_manager.to_specific_user(message)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)            
            print("error occurred")
            # await manager.broadcast(f"{user.username} left")@app.websocket("/api/user-chat/{receiver}")

@app.websocket("/api/room-chat/{room}")
async def room_chat(websocket: views.WebSocket, room: str, db: Session = Depends(get_db)):
    user = views.get_current_user(db, websocket.cookies.get("access_token"))
    if user:
        await socket_manager.connect(websocket, user)
        room = db.query(models.Room).filter(models.Room.name == room).first()
        RoomMessage = models.RoomMessage
        old_messages = db.query(RoomMessage).filter(
            RoomMessage.room_id == room.id
        ).order_by(RoomMessage.created_date).all()
        for message in old_messages:
            if message.sender_id == user.id:
                sender = user
            else:
                sender = db.query(models.User).filter(
                    models.User.id == message.sender_id
                ).first()
                sender = sender
            msg_data = {
                "id": message.id,
                "author": {
                    "username": sender.username,
                    "fullname": views.get_fullname(sender)
                },
                "message": message.text,
                "ist_date": views.get_timezone(message.created_date, "Asia/Kolkata") + " IST",
                "est_date": views.get_timezone(message.created_date, "US/Eastern")  + " EST",               
                "room": room.name,
                "user": user.username
            }
            if message.attachment_url:
                filename = message.attachment_url.split("/")[-1]
                msg_data.update({
                    "file": str(message.attachment_url),
                    "filename": filename
                })
            await socket_manager.populate_old_messages(msg_data)
        try:
            while True:
                data = await websocket.receive_json()
                file_data = data.get('file')
                if file_data:
                    file_size = file_data['size']
                    if file_size <= FILE_SIZE:
                        file = await websocket.receive_bytes()
                        filename = file_data['filename']
                        file_dir = views.gen_file_dir(room.name, __file__)
                        file_url = views.create_file(file_dir, filename, file)
                        data.update({
                            "file": file_url,
                            "filename": filename
                        })
                message = views.create_room_message(db, data)
                await socket_manager.to_room_participants(message)
        except WebSocketDisconnect:
            socket_manager.disconnect(websocket, user)
            # await manager.broadcast(f"{user.username} left")

            # ROOM ENDPOINTS

@app.post("/api/user/{id}/room")
async def create_room(request: Request, id: int, room_data: validators.CreateRoom, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        response = views.create_room(user, room_data, db)
        room = response['room']
        if room:
            response['participants'] = views.get_participants(room, db)
    else:
        response = {"error": "Unauthorized user"}
    return response


@app.get("/api/user/{id}/room")
def get_rooms(request: Request, id: int, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        response = views.get_rooms(user, db)
    else:
        response = {"error": "Unauthorized user"}
    return response


'''
    BISMA's CODE
'''

@app.delete("/api/user/personal-message/{id}")
async def del_msg(request: Request, id: int, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        db.query(models.PersonalMessage).filter(models.PersonalMessage.id == id).delete()
        db.commit()
        

@app.delete("/api/user/room-message/{id}")
async def del_msg(request: Request, id: int, db: Session = Depends(get_db)):
    user = views.get_current_user(db, request.cookies.get("access_token"))
    if user:
        db.query(models.RoomMessage).filter(models.RoomMessage.id == id).delete()
        db.commit()


# get user profile
@app.get("/api/profile/{id}")
def get_profile(id: int, db: Session = Depends(get_db)):
    print("show id")
    response = {
        "profile": {}        
    }
    user = db.query(models.User).filter(models.User.id == id).first()
    if user:
        full_name = user.first_name + " " + user.last_name
        username = user.username
        email = user.email
        join_date = user.created_date + " (UTC)"        

        profile = db.query(models.Profile).filter(models.Profile.id == id).first()
        

        response["profile"] = {
            "fullname": full_name,
            "username": username,
            "email": email,
            "join_date": join_date
        }
    else:
        response["error"] = "something went wrong."
    return response    
#  #   profile= await profile.get_user_by_email(db: Session =Depends(get), emai=profile.email)
#   #   if not profile:
#    	    raise HTTPException(
#        	status_code=HTTP_401_UNAUTHORIZED,
#        	detail="Incorrect email ,
#      )
#      else:
#          profile=profile.get_user_by_email(db)
#     return profile


#@app.get("/api/profile")
#def profile_update(db,email:str):
 #   up_profile= await profile.get_user_by_email(email =profile.email db: Session = Depends(get_db))
  #  if up_profile:
    #    return up_profile
    #else 
    #name = name
    #designation= designation
    #avatar= avatar
    #bio= bio

    #return profile