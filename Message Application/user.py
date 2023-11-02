

class User:
    def __init__(self):
        self.id = None
        
        self.first_name = None
        self.last_name = None

        self.chats = {}
    
    def set_name(self, first_name, last_name):
        self.first_name = first_name
        self.last_name = last_name

    def set_id(self, id):
        self.id = id