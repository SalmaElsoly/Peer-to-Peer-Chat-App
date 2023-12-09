import server.database as db
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
    
def logoutUser(username):
    db.deleteOne(db.CONNECTED_USER_COLLECTION, {"username": username})
    return 


    
    