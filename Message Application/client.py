import socket
import threading
import json

from settings import *

PORT = 55555
FORMAT = 'utf-8'
SERVER = '10.0.0.177'#'10.0.0.113'
HEADER = 64
ADDR = (SERVER, PORT)

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)



# usefull funcitons
def jsonify_data(**data):
    return json.dumps(data)

def reverse_jsonify(json_string):
    return json.loads(json_string)

# sending data
def send_data_to_server(func):
    def wrapper(*args):
        data = func(*args)
        encoded_data = data.encode(FORMAT)
        data_length = len(encoded_data)
        send_length = str(data_length).encode(FORMAT)
        send_length += b' ' * (HEADER - len(send_length))
        client.send(send_length)
        client.send(encoded_data)
        
    return wrapper
    

class Client:
    def __init__(self, app):
        self.app = app
        self.client_active = True

        self.commands = {
            'USER_INIT_REQUEST': self._perform_user_init_request_command,
            'NEW_USER': self._perform_new_user_command,
            'USER_LEFT': self._perform_user_left_command,
            'OTHER_USERS': self._perform_other_users_command,
            'USER_CHAT': self._perform_user_chat,
            'GLOBAL_CHAT': self._perform_global_chat
        }
    
    def close_connection_to_server(self):
        self.client_active = False
        client.close()
    
    def connect_to_server(self):
        try:
            client.connect(ADDR)
        except:
            print('[CONNECTION ERROR] Could not connect to server. Restarting process...')
            self.connect_to_server()
        else:
            thread = threading.Thread(target=self._receive)
            thread.start()
    
    @send_data_to_server
    def _send_user_init(self, user_first_name, user_last_name):
        return jsonify_data(command=USER_INIT_COMMAND, first_name=user_first_name, last_name=user_last_name)

    @send_data_to_server
    def send_user_chat(self, target_client, message):
        return jsonify_data(command=USER_CHAT_COMMAND, target_client=target_client, message=message)

    @send_data_to_server
    def send_global_chat(self, message):
        return jsonify_data(command=GLOBAL_CHAT_COMMAND, message=message)
    
    def _perform_user_chat(self, data: dict):
        client = data.get('client', None)
        message = data.get('message', '')
        self.app.add_message(client, message)

    def _perform_global_chat(self, data: dict):
        pass

    def _perform_user_init_request_command(self, data: dict):
        id = data['user_id']
        self.app.set_main_user_id(id)

        first_name, last_name = self.app.get_main_user_name()
        self._send_user_init(first_name, last_name)

    def _perform_new_user_command(self, data: dict):
        user_info: dict = data.get('user_info', {})
        user_id = list(user_info.keys())[0]
        first_name = user_info.get(user_id, {}).get('first_name', '')
        last_name = user_info.get(user_id, {}).get('last_name', '')
        address = user_info.get(user_id, {}).get('address', '')
        print(f'first name: {first_name} | last name: {last_name} | address: {address}')
        self.app.add_online_user(user_id, (first_name, last_name), address)
    
    def _perform_user_left_command(self, data: dict):
        user_id = data['user_id']
        self.app.remove_online_user(user_id)
        
    def _perform_other_users_command(self, data: dict):
        other_users = data.get('other_users', {})
        for user_id, user_info in other_users.items():
            name = (user_info.get('first_name'), user_info.get('last_name'))
            address = user_info.get('address')
            self.app.add_online_user(user_id, name, address)

    def _handle_incoming_data(self, data):
        command = data['command']
        print(command)

        if command in self.commands:
            self.commands[command](data)

    # handle connections
    def _receive(self):
        try:
            while self.client_active:
                data_length = client.recv(HEADER).decode(FORMAT)
                if data_length:
                    message_length = int(data_length)
                    data = reverse_jsonify(client.recv(message_length).decode(FORMAT))
                    print(data)
                    self._handle_incoming_data(data)
                    
        except:
            if self.client_active:
                print('[CONNECTION LOST] conneciton to server lost...')
                self.connect_to_server()
            else:
                print('client destroyd the connection to the server')
        
        

