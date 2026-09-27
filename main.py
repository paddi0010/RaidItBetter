import sys
from PySide6.QtWidgets import QApplication
from core.settings import load_language
from ui.main_window import TwitchRaidApp
from core.logger import setup_logger
import logging

logger = logging.getLogger("RaidItBetter")

def handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    logger.critical("Uncaught exception / Crash occurred:", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = handle_exception

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    lang = load_language()
    if not lang:
        lang = "en" 
            
    logger = setup_logger()
    logger.info("RaidItBetter started.")        
    
    window = TwitchRaidApp(lang)
    window.show()
    
    sys.exit(app.exec())