    def handle_hello_message(data, client_address):
   
    online_users[client_address] = time.time()

   
    while True:
        try:
            
            message, address = server_socket.recvfrom(1024).decode()

            if message == 'HELLO':
              
                online_users[client_address] = time.time()

               

        except socket.error:
           
            print(f"User at {client_address} disconnected.")

           
            username = get_username(client_address)
            logoutUser(username)
            break

def check_users():
    while True:
        # Check the last seen timestamp for each user
        current_time = time.time()
        disconnected_users = []

        for client_address, last_seen in online_users.items():
            if current_time - last_seen > 3:
                # User has not sent a 'HELLO' message for 3 seconds, consider them disconnected
                disconnected_users.append(client_address)

       
        for user in disconnected_users:
            del online_users[user]
            print(f"User at {user} disconnected.")

           
            username = get_username(user)
            logoutUser(username)

      
        time.sleep(1)
