import customtkinter as ctk
from settings import load_language
from ui.main_window import LanguageSelectDialog, TwitchRaidApp

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

if __name__ == "__main__":
    lang = load_language()
    if not lang:
        dialog = LanguageSelectDialog()
        dialog.mainloop()
        lang = load_language()
        if not lang:
            lang = "de"
            
    app = TwitchRaidApp(lang)
    app.mainloop()