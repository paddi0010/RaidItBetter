import customtkinter as ctk
from core.settings import APP_VERSION

class Aboutwindow(ctk.CTkFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=("gray95", "gray15"), corner_radius=0, width=400)
        self.app = app_controller
        self.t = app_controller.t
        self.pack_propagate(False)
        
        # Header
        self.lbl_header = ctk.CTkLabel(self, text=self.t.get("about_title", "ℹ️ Über RaidItBetter"), font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_header.pack(pady=20, padx=20, anchor="w")
        
        # Info Text
        self.lbl_version = ctk.CTkLabel(self, text=f"Version: {APP_VERSION}", font=ctk.CTkFont(size=13, weight="bold"))
        self.lbl_version.pack(padx=20, anchor="w", pady=(10, 5))
        
        desc_text = (
            "Ein simples Tool zum Verwalten von Raids \n\n"
            "Dev: Paddi0010"
        )
        
        self.lbl_desc = ctk.CTkLabel(self, text=desc_text, font=ctk.CTkFont(size=12), justify="left", wraplength=360)
        self.lbl_desc.pack(padx=20, anchor="w", pady=(5, 20))
        
        # Close Button
        self.btn_close = ctk.CTkButton(
            self, text=self.t.get("close", "Schließen"),
            fg_color=("gray80", "gray30"), hover_color=("gray70", "gray40"),
            text_color=("black", "white"),
            command=self.app.toggle_about
        )
        self.btn_close.pack(side="bottom", fill="x", padx=20, pady=20)
        
    def update_texts(self):
        self.t = self.app.t
        self.lbl_header.configure(text=self.t.get("about_title", "ℹ️ Über RaidItBetter"))
        self.btn_close.configure(text=self.t.get("close", "Schließen"))