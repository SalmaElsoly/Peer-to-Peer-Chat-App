import database as db
import json

def createChatroom(roomname):
    if(db.findOne(db.ROOM_COLLECTION, {"roomname": roomname})):
        return "create-chat-room-exists"
    else:
        room = {"roomname": roomname, "users": []}
        db.insertOne(db.ROOM_COLLECTION, room)
        return "create-chat-room-success"
 
def listChatRooms():
    chatRooms = db.findAll(db.ROOM_COLLECTION)
    rooms = []
    for room in chatRooms:
        rooms.append((room['roomname'],len(room['users'])))
    return rooms

def joinChatRoom(roomname, username, ip, port):
    room = db.findOne(db.ROOM_COLLECTION, {"roomname": roomname})
    if(room):
        if(db.findOne(db.ROOM_COLLECTION, {"username": username})):
            return "join-chat-room-online"
        else:
            db.addUserToRoom(roomname, username, ip, port)
            #get all users in the room except the user itself
            users = db.getUsersInRoom(roomname)
            users.remove({"username":username,"ip":ip,"port":port})
            return "join-chat-room-success" + " " + json.dumps(users)
    else: 
        return "join-chat-room-not-exist"

def leaveChatRoom(roomname, username):
    result = db.removeUserFromRoom(roomname, username)
    if result.acknowledged:
        return "Leave-chat-room-success"
    else:
        return "leave-chat-room-not successful"
