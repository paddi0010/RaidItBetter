import os
import sys
import json

def get_base_path():
    if getattr(sys, 'frozen', False):
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))

def get_config_dir():
    appdata = os.getenv('APPDATA')
    if appdata:
        path = os.path.join(appdata, "RaidItBetter")
        os.makedirs(path, exist_ok=True)
        return path
    return get_base_path()

CONFIG_FILE = os.path.join(get_config_dir(), "settings.json")

def load_language():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data.get("language")
        except Exception:
            pass
    return None

def save_language(lang):
    try:
        data = {}
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
        data["language"] = lang
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        print(f"Fehler beim Speichern der Sprache: {e}")

def load_translations(lang):
    base_path = get_base_path()
    file_path = os.path.join(base_path, "locales", f"{lang}.json")
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"Fehler beim Laden der Sprachdatei {file_path}: {e}")
        return {}