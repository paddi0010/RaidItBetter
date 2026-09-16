import customtkinter as ctk

class SettingsPanel(ctk.CTkFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent, fg_color=("gray95", "gray15"), corner_radius=0, width=400)
        self.app = app_controller
        self.t = app_controller.t 
        self.pack_propagate(False)

        # Header
        self.lbl_header = ctk.CTkLabel(self, text=self.t.get("settings_title", "⚙️ Einstellungen"), font=ctk.CTkFont(size=16, weight="bold"))
        self.lbl_header.pack(pady=20, padx=20, anchor="w")

        # Language-Settings
        self.lbl_lang = ctk.CTkLabel(self, text=self.t.get("settings_language", "Sprache / Language:"), font=ctk.CTkFont(size=12))
        self.lbl_lang.pack(padx=20, anchor="w", pady=(10, 5))

        current_choice = "Deutsch" if getattr(self.app, "lang", "de") == "de" else "English"
        self.lang_menu = ctk.CTkOptionMenu(
            self, values=["Deutsch", "English"],
            command=self.on_language_change
        )
        self.lang_menu.pack(padx=20, anchor="w", pady=(0, 20))
        self.lang_menu.set(current_choice)

        # Close-Button
        self.btn_close = ctk.CTkButton(
            self, text=self.t.get("close", "Schließen"), 
            fg_color=("gray80", "gray30"), hover_color=("gray70", "gray40"),
            text_color=("black", "white"),
            command=self.app.toggle_settings
        )
        self.btn_close.pack(side="bottom", fill="x", padx=20, pady=20)

    def on_language_change(self, choice):
        lang_code = "de" if choice == "Deutsch" else "en"
        if hasattr(self.app, "change_language"):
            self.app.change_language(lang_code)
            self.update_texts()

    def update_texts(self):
        self.t = self.app.t
        self.lbl_header.configure(text=self.t.get("settings_title", "⚙️ Einstellungen"))
        self.lbl_lang.configure(text=self.t.get("settings_language", "Sprache / Language:"))
        self.btn_close.configure(text=self.t.get("close", "Schließen"))