import sys
import argparse
from PySide6.QtWidgets import QApplication, QMessageBox
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
    
    try:
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Critical)
        msg.setWindowTitle("Critical Error")
        msg.setText("An unexpected error has occurred.")
        msg.setDetailedText(str(exc_value))
        msg.exec()
    except Exception:
        pass

sys.excepthook = handle_exception

def parse_arguments():
    parser = argparse.ArgumentParser(description="TwitchRaidApp - RaidItBetter")
    parser.add_argument("--debug", action="store_true", help="Enables extended console logging")
    return parser.parse_args()

if __name__ == "__main__":
    args = parse_arguments()
    
    app = QApplication(sys.argv)
    app.setApplicationName("RaidItBetter")
    app.setOrganizationName("Paddi0010")
    
    lang = load_language()
    if not lang:
        lang = "en" 
            
    logger = setup_logger()
    logger.info("RaidItBetter started.")
    
    if args.debug:
        logger.info("Debug mode enabled via command line.")
    
    window = TwitchRaidApp(lang)
    window.show()
    
    sys.exit(app.exec())