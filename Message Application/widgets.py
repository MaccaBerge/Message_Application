import tkinter as tk
import customtkinter as ctk
from PIL import Image
from typing_extensions import Literal

from settings import *


class Entry(ctk.CTkFrame):
    def __init__(self, master, width=50, padx=0, pady=0, corner_radius=10,
                 font=('font1', 12), bg_color='white', text_color='black',
                 border_width=0, border_color='grey80', max_height=13, custom_return=None,
                 placeholder_text='Send a message...'):

        super().__init__(master=master, fg_color=bg_color, corner_radius=corner_radius,
                         border_width=border_width, border_color=border_color)
        
        self.custom_return = custom_return

        # Textbox
        self.text_widget = tk.Text(self, width=width, height=1, padx=padx, pady=pady, 
                                   wrap='word', font=font, foreground=text_color,
                                   borderwidth=0)
        self.text_widget.pack(side='left', padx=20, pady=20)
        self.text_widget.bind('<<Modified>>', self._update_text_height)
        self.text_widget.bind('<Return>', self._call_custom_return)
        self.text_widget.bind('<FocusIn>', self._on_focus_in)
        self.text_widget.bind('<FocusOut>', self._on_focus_out)
        self.max_height = max_height

        self.placeholder_text = placeholder_text
        self._add_placeholder_text(self.placeholder_text)
        
        # scrollbar
        self.scrollbar = ctk.CTkScrollbar(self, command=self.text_widget.yview, 
                                          button_color=SCROLLBAR_COLOR, 
                                          button_hover_color=SCROLLBAR_HOVER_COLOR)
        self.scrollbar_state = False

    def _update_text_height(self, event):
        num_lines = self._get_display_lines()

        if num_lines <= self.max_height:
            self.text_widget.configure(height=num_lines)
        elif num_lines > self.max_height and not self.placeholder_text_active:
            self.text_widget.configure(height=self.max_height)

        if num_lines > self.max_height and self.scrollbar_state is False and not self.placeholder_text_active:
            self.scrollbar.pack(side='left', fill='y', pady=10)
            self.text_widget['yscrollcommand'] = self.scrollbar.set
            self.scrollbar_state = True
        elif num_lines <= self.max_height and self.scrollbar_state is True:
            self.scrollbar.pack_forget()
            self.scrollbar_state = False
        
        self.text_widget.edit_modified(False)

    def _call_custom_return(self, event):
        if self.custom_return:
            self.custom_return()
        return 'break'
    
    def _on_focus_in(self, event):
        if self.placeholder_text_active:
            self._remove_placeholder_text()
            
    def _on_focus_out(self, event):
        if self.text_widget.get('1.0', 'end-1c') == '':
            self._add_placeholder_text(self.placeholder_text)
    
    def _add_placeholder_text(self, text: str, color=ENTRY_PLACEHOLDER_COLOR):
        self.text_widget.configure(fg=color)
        self.text_widget.insert('1.0', text)
        self.placeholder_text_active = True
    
    def _remove_placeholder_text(self):
        self.text_widget.delete('1.0', 'end')
        self.text_widget.configure(fg='black')
        self.placeholder_text_active = False
    
    def _get_display_lines(self) -> int:
        num_lines = self.text_widget.count('1.0', 'end', 'displaylines')[0]
        return num_lines

    def get_text(self) -> str:
        return self.text_widget.get('1.0', 'end').strip()
    
    def clear(self):
        self.text_widget.delete('1.0', 'end')
   
class Search(ctk.CTkFrame):
    def __init__(self, master, entry_width=150, border_width=0, placeholder_text='Search...', 
                 placeholder_text_color=SEARCH_PLACEHOLDER_COLOR, text_color='black', 
                 font=('', 16), color=SEARCH_COLOR, corner_radius=15, width=200):
        super().__init__(master=master, width=width, height=40, fg_color=color, corner_radius=corner_radius)

        self.entry = ctk.CTkEntry(master=self, width=entry_width, border_width=border_width, 
                         placeholder_text=placeholder_text, placeholder_text_color=placeholder_text_color, 
                         text_color=text_color, fg_color=color, font=font)
        self.entry.place(x=25, rely=0.5, relwidth=0.8, anchor='w')

        # search icon
        self.contact_icon = ctk.CTkImage(Image.open('Graphics/search.png'), size=(SEARCH_ICON_SIZE))
        self.icon = ctk.CTkLabel(self, image=self.contact_icon, text='')
        self.icon.place(x=20, rely=0.5, anchor='center')

class Online_Users(ctk.CTkScrollableFrame):
    def __init__(self, master, button_func):
        super().__init__(master=master, fg_color=MENU_BAR_COLOR, scrollbar_button_color=SCROLLBAR_COLOR, 
                         scrollbar_button_hover_color=SCROLLBAR_HOVER_COLOR)
        
        self.user_button_pressed = button_func
        self.online_users = {}
        self.contact_icon = ctk.CTkImage(Image.open('Graphics/user.png'), size=USER_ICON_SIZE)


    def _add_user_button(self, name: str, id: str):
        first_name, last_name = str(name[0]), str(name[1])
        button = ctk.CTkButton(self, text=f'{first_name} {last_name}', image=self.contact_icon, height=90,
                      fg_color='transparent', hover_color=MENU_BAR_SHADE_COLOR,
                      text_color='black', anchor='w', corner_radius=10, command=lambda: self.user_button_pressed(id))
        button.pack(fill='x', padx=10)
        return button
    
    def add_user(self, id: str, name: str, address: str):
        button = self._add_user_button(name, id)
        self.online_users[id] = {'name': name, 'address': address, 'button': button}
    
    def remove_user(self, id: str):
        if id in self.online_users:
            user_info = self.online_users.get(id, {})
            user_button = user_info.get('button')
            user_button.pack_forget()
            self.online_users.pop(id)
        
class Chat(ctk.CTkScrollableFrame):
    def __init__(self, master, *args, **kwargs):
        super().__init__(master=master, *args, **kwargs)
        self.side_spesifications = {'left': {'boubble_color': OTHER_USERS_TEXT_BOUBBLE_COLOR, 'text_color': 'black'}, 
                                    'right': {'boubble_color': MAIN_USER_TEXT_BOUBBLE_COLOR, 'text_color': 'white'}}
    
    def add_message(self, message: str, side: Literal['left', 'right']):
        frame = ctk.CTkFrame(self, fg_color='transparent')
        frame.pack(fill='x', pady=10, padx=100)
        message_boubble = Message_Boubble(frame, message, boubble_color=self.side_spesifications[side]['boubble_color'], text_color=self.side_spesifications[side]['text_color'])
        message_boubble.pack(side=side)

        if side == MAIN_USER_CHAT_SIDE:
            self.autoscroll_bottom()
    
    def autoscroll_bottom(self):
        self._parent_canvas.update_idletasks()
        self._parent_canvas.yview_moveto(1)


class Message_Boubble(ctk.CTkFrame):
    def __init__(self, master, text: str, text_color: str='black', text_size:int=18, text_padx:int=10, text_pady:int=10, boubble_color:str=SIGN_UP_BG_COLOR):
        super().__init__(master=master, fg_color=boubble_color)

        self.label = ctk.CTkLabel(self, text=text, text_color=text_color, fg_color='transparent', font=('', text_size), justify='left', wraplength=600)
        self.label.pack(expand=True, fill='x', padx=text_padx, pady=text_pady)
    
    def change_wrap_length(self, new_wrap_length):
        self.label.configure(wraplength=new_wrap_length)