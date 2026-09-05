import requests
import webbrowser
from tkinter import messagebox

GITHUB_REPO = "paddi0010/RaidItBetter"
CURRENT_VERSION = "0.2.1 alpha"

def check_update_status():
    url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
    try:
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            latest_version = data.get("tag_name", "").strip()
            release_url = data.get("html_url")
            
            # Normalisieren: Alles in Kleinbuchstaben, 'v' am Anfang entfernen, Bindestriche/Leerzeichen entfernen
            clean_latest = latest_version.lower().lstrip('v').replace('-', '').replace(' ', '')
            clean_current = CURRENT_VERSION.lower().lstrip('v').replace('-', '').replace(' ', '')
            
            # Zum Testen kannst du die Zeile hier auskommentieren (Print schauen in der Konsole)
            # print(f"Vergleich: GitHub='{clean_latest}' vs Lokal='{clean_current}'")
            
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
        msg = (f"Eine neue Version ist verfügbar!\n"
               f"Deine aktuelle Version: {CURRENT_VERSION}\n\n"
               "Möchtest du die Release-Seite im Browser öffnen, um das Update herunterzuladen?")
        if messagebox.askyesno("Update verfügbar", msg, parent=parent_window):
            webbrowser.open(release_url)
    elif release_url:
        if not silent:
            messagebox.showinfo("Kein Update", "Du verwendest bereits die neueste Version.", parent=parent_window)
    else:
        if not silent:
            messagebox.showwarning("Hinweis", "Es konnten keine Update-Informationen von GitHub abgerufen werden (evtl. existiert noch kein Release).", parent=parent_window)