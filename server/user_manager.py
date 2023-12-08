import server.database as db
"""Create a new user account."""
def createAccount(username, password):
    if(db.findOne(db.USER_ACCOUNT_COLLECTION, {"username": username})):
        return "join-exists"
    else:
        hashed_password = hashPassword(password)
        user = {"username": username, "password": hashed_password}
        db.insertOne(db.USER_ACCOUNT_COLLECTION, user)
        return "join-success"
    
def logoutUser(username):
    db.deleteOne(db.CONNECTED_USER_COLLECTION, {"username": username})
    return 
    