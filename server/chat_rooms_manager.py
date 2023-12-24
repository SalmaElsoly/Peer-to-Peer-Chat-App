import database as db

def createChatroom(roomname, username, ip, port):
    if(db.findOne(db.ROOM_COLLECTION, {"roomname": roomname})):
        return "create-chat-room-exists"
    else:
        room = {"roomname": roomname, "username": username, "ip": ip, "port": port}
        db.insertOne(db.ROOM_COLLECTION, room)
        return "create-chat-room-success"
 
def listChatRooms():
    chatRooms = db.findAll(db.ROOM_COLLECTION)
    rooms = []
    for room in chatRooms:
        rooms.append((room['roomname'],len(room['users'])))
    return rooms