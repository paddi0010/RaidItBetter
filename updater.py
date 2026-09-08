import requests
import webbrowser
from tkinter import messagebox

GITHUB_REPO = "paddi0010/RaidItBetter"
CURRENT_VERSION = "0.3.2 alpha"

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
        if messagebox.askyesno("Update available", msg, parent=parent_window):
            webbrowser.open(release_url)
    elif release_url:
        if not silent:
            messagebox.showinfo("No Update", "You are already using the latest version.", parent=parent_window)
    else:
        if not silent:
            messagebox.showwarning("Notice", "Could not retrieve update information from GitHub (possibly no release exists).", parent=parent_window)