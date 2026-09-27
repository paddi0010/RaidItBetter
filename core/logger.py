import logging
import os
import sys

def setup_logger():
    if sys.platform == "win32":
        base_dir = os.path.join(os.environ.get("APPDATA", ""), "RaidItBetter")
    else:
        base_dir = os.path.expanduser("~/.raiditbetter")

    os.makedirs(base_dir, exist_ok=True)
    log_file = os.path.join(base_dir, "app.log")

    logger = logging.getLogger("RaidItBetter")
    logger.setLevel(logging.DEBUG)

    if not logger.handlers:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
        file_handler.setFormatter(file_formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter("[%(levelname)s] %(message)s")
        console_handler.setFormatter(console_formatter)

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger