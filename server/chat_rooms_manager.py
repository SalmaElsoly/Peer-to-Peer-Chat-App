import database as db
import json


def createChatroom(roomname):
    if db.findOne(db.ROOM_COLLECTION, {"roomname": roomname}):
        return "create-chat-room-exists"
    else:
        room = {"roomname": roomname, "users": []}
        db.insertOne(db.ROOM_COLLECTION, room)
        return "create-chat-room-success"


def listChatRooms():
    chatRooms = db.findAll(db.ROOM_COLLECTION)
    rooms = []
    for room in chatRooms:
        rooms.append((room["roomname"], len(room["users"])))
    return rooms


def joinChatRoom(roomname, username, tcpThreads):
    room = db.findOne(db.ROOM_COLLECTION, {"roomname": roomname})
    if room:
        if db.findOne(db.ROOM_COLLECTION, {"username": username}):
            return "join-chat-room-online"
        else:
            db.addUserToRoom(roomname, username)
            # get all users in the room except the user itself
            users = db.getUsersInRoom(roomname)
            users.remove({"username": username})
            usersList = []
            for user in users:
                usersList.append(
                    (
                        user["username"],
                        tcpThreads[user["username"]].udpAddress[0],
                        str(tcpThreads[user["username"]].udpAddress[1]),
                    )
                )
            return usersList
            
    else:
        return None


def leaveChatRoom(roomname, username, tcpThreads):
    result = db.removeUserFromRoom(roomname, username)
    if result.acknowledged:
         users = db.getUsersInRoom(roomname)
         usersList = []
         for user in users:
            usersList.append(
                (
                    user["username"],
                    tcpThreads[user["username"]].udpAddress[0],
                    str(tcpThreads[user["username"]].udpAddress[1]),
                )
            )
            return usersList
       
    else:
        return None
