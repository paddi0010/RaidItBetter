import requests
import webbrowser
from PySide6.QtWidgets import QMessageBox
from core.settings import APP_VERSION

GITHUB_REPO = "paddi0010/RaidItBetter"
CURRENT_VERSION = f"{APP_VERSION}"

def check_update_status():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("tag_name", "").strip()
            release_url = data.get("html_url")
            clean_latest = latest_version.lower().lstrip('v').replace('-', '').replace(' ', '')
            clean_current = CURRENT_VERSION.lower().lstrip('v').replace('-', '').replace(' ', '')
            
            if clean_latest and clean_latest != clean_current:
                return True, release_url
            return False, release_url
        else:
            return False, ""
    except Exception as e:
        print(f"Update-Status-Check fehlgeschlagen: {e}")
        return False, ""

def check_for_updates(parent_window=None, silent=False):
    has_update, release_url = check_update_status()
    
    if has_update:
        msg = (f"A new version is available!\n"
               f"Your current version: {CURRENT_VERSION}\n\n"
               "Would you like to open the release page in your browser to download the update?")
        
        reply = QMessageBox.question(
            parent_window, 
            "Update available", 
            msg, 
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
            QMessageBox.StandardButton.Yes
        )
        if reply == QMessageBox.StandardButton.Yes:
            if release_url:
                webbrowser.open(release_url)
                
    elif release_url:
        if not silent:
            QMessageBox.information(
                parent_window, 
                "No Update", 
                "You are already using the latest version."
            )
    else:
        if not silent:
            QMessageBox.warning(
                parent_window, 
                "Notice", 
                "Could not retrieve update information from GitHub (possibly no release exists)."
            )