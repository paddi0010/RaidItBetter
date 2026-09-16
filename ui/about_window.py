import webbrowser
import customtkinter as ctk
from ui.styles import COLOR_PRIMARY, COLOR_PRIMARY_HOVER, BG_CARD, get_font_title, get_font_bold
from core.settings import APP_VERSION
from ui.settings_window import SettingsPanel

class Aboutwindow(ctk.CTkToplevel):
    def __init__(self, parent, translations):
        super().__init__(parent)
        self.t = translations
        self.title("RaidItBetter - About")
        
        width = 380
        height = 360
        self.resizable(False, False)
        
        self.transient(parent)
        self.grab_set()
        
        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()
        
        x = parent_x + (parent_w // 2) - (width // 2)
        y = parent_y + (parent_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")
        
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        lbl_version = ctk.CTkLabel(content_frame, text=f"{APP_VERSION}", font=get_font_bold(12), text_color="gray")
        lbl_version.pack(pady=(0, 15))
        
        desc_text = (
            "Ein simples Tool zum Verwalten von Raids \n\n"
            "Dev: Paddi0010"
        )
        
        lbl_desc = ctk.CTkLabel(content_frame, text=desc_text, font=ctk.CTkFont(size=12), justify="center", wraplength=320)
        lbl_desc.pack(pady=(0, 20))
        
        btn_github = ctk.CTkButton(
            content_frame, text="🌐 GitHub Repository", 
            fg_color=COLOR_PRIMARY, hover_color=COLOR_PRIMARY_HOVER,
            font=get_font_bold(12), height=35,
            command=lambda: webbrowser.open("https://github.com/paddi0010/RaidItBetter")
        )
        btn_github.pack(fill="x", pady=(0, 10))
            
        btn_close = ctk.CTkButton(
            content_frame, text="Schließen",
            fg_color=("gray80", "gray30"), hover_color=("gray70", "gray40"),
            text_color=("black", "white"),
            font=get_font_bold(12), height=32,
            command=self.destroy
        )
        btn_close.pack(fill="x")