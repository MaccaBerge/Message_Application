import customtkinter as ctk

from settings import *
from widgets import Entry, Search, Online_Users, Chat
from user import User
from client import Client

class App(ctk.CTk):
    def __init__(self, size = WINDOW_SIZE, title = WINDOW_TITLE):
        super().__init__()
        self.geometry(f'{size[0]}x{size[1]}')
        self.minsize(int(WINDOW_SIZE[0]), int(WINDOW_SIZE[1]))
        self.configure(fg_color=MENU_BAR_SHADE_COLOR)
        self.protocol('WM_DELETE_WINDOW', self.quit_application)
        self.title(str(title))
        #self.wm_attributes('-alpha', 0.96)

        self.client = Client(self)
        self.main_user = User()

        self.users = {}
        self.selected_user_chat = 'global'

        self._create_sign_up()
    
    def quit_application(self):
        self.client.close_connection_to_server()
        self.destroy()

    def _create_main_application(self):

        # user menu
        self.main_frame_left = ctk.CTkFrame(self, fg_color='transparent', width=350)
        self.main_frame_left.pack_propagate(False)
        self.main_frame_left.pack(side='left', fill='y')

        # search field
        self.search_frame = ctk.CTkFrame(self.main_frame_left, fg_color=MENU_BAR_COLOR, height=100)
        self.search_frame.pack_propagate(False)
        self.search = Search(self.search_frame, width=250, corner_radius=20)
        self.search.place(rely=0.5, relx=0.5, anchor='c')
        self.search_frame.pack(fill='x')

        self.online_users_frame = ctk.CTkFrame(self.main_frame_left, fg_color=MENU_BAR_COLOR, corner_radius=0)
        self.online_users_frame.pack_propagate(False)
        self.online_users_widget = Online_Users(self.online_users_frame, self.user_button_pressed)
        self.online_users_widget.pack(expand=True, fill='both')
        self.online_users_frame.pack(expand=True, fill='both')

        # user info
        self.user_info_menu_frame = ctk.CTkFrame(self, fg_color=MENU_BAR_COLOR, corner_radius=0, height=100)
        self.user_info_menu_frame.pack_propagate(False)
        self.user_info_menu_frame.pack(side='top', fill='x')
        self.user_info_name_label = ctk.CTkLabel(self.user_info_menu_frame, text='', font=('', 30, 'bold'))
        self.user_info_name_label.place(relx=0.5, rely=0.5, anchor='center')

        # chat
        self.chat_frame = ctk.CTkFrame(master=self, fg_color=MENU_BAR_SHADE_COLOR)
        self.chat_frame.pack(expand=True, fill='both')

        self.entry_frame = ctk.CTkFrame(self, fg_color=MENU_BAR_SHADE_COLOR)
        self.entry_frame.pack(side='bottom', fill='x')
        self.entry = Entry(self.entry_frame, width=100, corner_radius=20, custom_return=self._send_message)
        self.entry.pack(pady=10)

    def _create_sign_up(self):
        self.sign_up_frame = ctk.CTkFrame(self, fg_color=SIGN_UP_BG_COLOR, width=700, height=600)
        self.sign_up_frame.place(relx=0.5, rely=0.5, anchor='center')

        self.sign_up_label = ctk.CTkLabel(self.sign_up_frame, text='Sign Up', text_color='white', font=('', 50, 'bold'))
        self.sign_up_label.place(relx=0.5, rely=0.1, anchor='n')

        self.first_name_entry = ctk.CTkEntry(self.sign_up_frame, width=450, height=55, border_width=0, font=('font1', 17), 
                                       corner_radius=10, placeholder_text='First Name', 
                                       placeholder_text_color=ENTRY_PLACEHOLDER_COLOR)
        self.first_name_entry.place(relx=0.5, rely=0.425, anchor='center')

        self.last_name_entry = ctk.CTkEntry(self.sign_up_frame, width=450, height=55, border_width=0, font=('font1', 17),
                                       corner_radius=10, placeholder_text='Last Name', 
                                       placeholder_text_color=ENTRY_PLACEHOLDER_COLOR)
        self.last_name_entry.place(relx=0.5, rely=0.575, anchor='center')

        self.done_button = ctk.CTkButton(self.sign_up_frame, text='Done', fg_color='transparent', hover_color=SIGN_UP_BUTTON_HOVER_COLOR, 
                                         text_color='white', font=('font1', 17, 'bold'), corner_radius=100, border_width=2, border_color='white',
                                         height=40, command=self._sign_up_done)
        self.done_button.place(relx=0.5, rely=0.8, anchor='center')

    def _send_message(self):
        print(f'Message "{self.entry.get_text()}" sent to {self.selected_user_chat} | type: {type(self.selected_user_chat)}')
        message = self.entry.get_text()
        if self.selected_user_chat == 'global':
            pass
        else:
            self.client.send_user_chat(self.selected_user_chat, message)
        self.entry.clear()

        self.main_user.chats[self.selected_user_chat].add_message(message, MAIN_USER_CHAT_SIDE)

    def _sign_up_done(self):
        first_name = self.first_name_entry.get()
        last_name = self.last_name_entry.get()

        self.main_user.set_name(first_name, last_name)

        # load the main application
        self.sign_up_frame.destroy()
        self._create_main_application()

        self.client.connect_to_server() # got to find a better solution
    
    def _display_new_user_chat(self):
        for widget in self.chat_frame.winfo_children():
            widget.pack_forget()
        new_chat = self.main_user.chats[self.selected_user_chat]
        print(self.main_user.chats)
        new_chat.pack(expand=True, fill='both')
    
    def get_main_user_name(self):
        return self.main_user.first_name, self.main_user.last_name
    
    def set_main_user_id(self, id):
        self.main_user.set_id(id)
    
    def add_online_user(self, id, name, address):
        self.online_users_widget.add_user(str(id), name, address)
        self.main_user.chats[id] = Chat(self.chat_frame, fg_color=MENU_BAR_SHADE_COLOR, scrollbar_button_color=SCROLLBAR_COLOR, scrollbar_button_hover_color=SCROLLBAR_HOVER_COLOR)

    def remove_online_user(self, id):
        self.online_users_widget.remove_user(str(id))
    
    def user_button_pressed(self, user_id):
        name = self.online_users_widget.online_users[user_id]['name']
        self.user_info_name_label.configure(text=name)

        if self.selected_user_chat != user_id:
            self.selected_user_chat = user_id
            self._display_new_user_chat()
            self.main_user.chats[self.selected_user_chat].autoscroll_bottom()
    
    def add_message(self, target_user, message):
        self.main_user.chats[target_user].add_message(message, OTHER_USERS_CHAT_SIDE)
    
if __name__ == '__main__':
    app = App()
    app.mainloop()






