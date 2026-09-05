import customtkinter as ctk
from ui.styles import FONT_MAIN

class UpdateSection(ctk.CTkFrame):
    def __init__(self, master, update_command, **kwargs):
        super().__init__(master, **kwargs)
        
        self.configure(fg_color="transparent")
        
        self.btn_update = ctk.CTkButton(
            self, 
            text="Update prüfen", 
            font=FONT_MAIN,
            command=update_command
        )
        self.btn_update.pack(padx=10, pady=10)