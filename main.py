import customtkinter as ctk
import sys
from core.settings import load_language
from ui.main_window import LanguageSelectDialog, TwitchRaidApp
from core.logger import setup_logger
import logging

logger = logging.getLogger("RaidItBetter")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    
    logger.critical("Uncaught exception / Crash occurred:", exc_info=(exc_type, exc_value, exc_traceback))

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")
sys.excepthook = handle_exception

if __name__ == "__main__":
    lang = load_language()
    if not lang:
        dialog = LanguageSelectDialog()
        dialog.mainloop()
        lang = load_language()
        if not lang:
            lang = "en"
            
    logger = setup_logger()
    logger.info("RaidItBetter started.")        
    app = TwitchRaidApp(lang)
    app.mainloop()
    