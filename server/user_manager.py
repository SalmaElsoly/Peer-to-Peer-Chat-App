import database as db
from pyargon2 import hash

CONST_SALT = "23LUCKY55;-)"
def hashPassword(username, password):
    # salt is combination of CONST_SALT and username 
    # salt must be unique and >= 8 in length
    salt = CONST_SALT + username    
    return hash(password, salt)

"""Create a new user account."""
def createAccount(username, password):
    if(db.findOne(db.USER_ACCOUNT_COLLECTION, {"username": username})):
        return "join-exists"
    else:
        hashed_password = hashPassword(username, password)
        user = {"username": username, "password": hashed_password}
        db.insertOne(db.USER_ACCOUNT_COLLECTION, user)
        return "join-success"

def loginUser(username, password, ip, port):
    user = db.findOne(db.USER_ACCOUNT_COLLECTION, {"username": username})
    if(user):
        if(db.findOne(db.CONNECTED_USER_COLLECTION, {"username": username})):
            return "login-online"
        elif(user["password"] != hashPassword(username,password)):
            return "login-wrong-credentials"
        else:
            # store username - !!! ip - !!! port 
            connected_user = {"username": username, "ip": ip, "port": port}
            db.insertOne(db.CONNECTED_USER_COLLECTION, connected_user)
            return "login-success"
    else: 
        return "login-account-not-exist"

def logoutUser(username):
    db.deleteOne(db.CONNECTED_USER_COLLECTION, {"username": username})
    return 

def getOnlineUsers(username):
    online_users = db.findAll(db.CONNECTED_USER_COLLECTION)
    users = []
    for user in online_users:
        if user['username'] == username:
            continue
        users.append((user['username'],user['ip'],user['port']))
    return users

def searchUser(username):
    user = db.findOne(db.CONNECTED_USER_COLLECTION, {"username": username})
    if(user):
        return user
    else:
        return "user-not-online"