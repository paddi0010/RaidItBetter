import json
import os
import re
import threading
import customtkinter as ctk
from config import FAVS_FILE
from twitch_api import TwitchClient

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("dark-blue")

class TwitchRaidApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.twitch = TwitchClient()
        self.favorites = self.load_favorites()

        self.title("RaidItBetter")
        self.geometry("380x430")
        self.resizable(False, False)

        self.title_label = ctk.CTkLabel(self, text="⚡ RaidItBetter", font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(pady=(20, 10))

        login_text = "✅ Eingeloggt (Neu einloggen)" if self.twitch.access_token else "Mit Twitch einloggen"
        login_color = "#2b2b2b" if self.twitch.access_token else "#9146FF"
        
        self.btn_login = ctk.CTkButton(self, text=login_text, fg_color=login_color, hover_color="#772ce8", width=280, height=35, command=self.handle_login)
        self.btn_login.pack(pady=5)

        self.entry_streamer = ctk.CTkEntry(self, placeholder_text="Streamer-Name eingeben...", width=280, height=40)
        self.entry_streamer.pack(pady=5)

        self.btn_add_fav = ctk.CTkButton(self, text="⭐ Als Favorit speichern", fg_color="#333333", hover_color="#444444", width=280, height=30, command=self.add_favorite)
        self.btn_add_fav.pack(pady=5)

        self.fav_dropdown = ctk.CTkComboBox(self, values=self.get_dropdown_values(), command=self.on_fav_selected, width=280, height=35)
        self.fav_dropdown.pack(pady=10)

        self.btn_raid = ctk.CTkButton(self, text="RAID STARTEN", fg_color="#e91916", hover_color="#c81310", width=280, height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.on_raid_click)
        self.btn_raid.pack(pady=10)

        self.label_status = ctk.CTkLabel(self, text="Bereit.", text_color="gray", font=ctk.CTkFont(size=12))
        self.label_status.pack(pady=(5, 15))

    def load_favorites(self):
        if os.path.exists(FAVS_FILE):
            try:
                with open(FAVS_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except:
                return []
        return []

    def save_favorites(self):
        with open(FAVS_FILE, "w", encoding="utf-8") as f:
            json.dump(self.favorites, f, ensure_ascii=False, indent=4)

    def get_dropdown_values(self):
        if not self.favorites:
            return ["-- Favoriten wählen --"]
        return ["-- Favoriten wählen --"] + self.favorites

    def update_dropdown(self):
        self.fav_dropdown.configure(values=self.get_dropdown_values())
        self.fav_dropdown.set("-- Favoriten wählen --")

    def add_favorite(self):
        name = self.entry_streamer.get().strip().lower()
        if not name:
            self.label_status.configure(text="❌ Erst Namen eingeben zum Speichern!", text_color="orange")
            return
        
        if not re.match(r"^\w{1,25}$", name):
            self.label_status.configure(text="❌ Ungültiger Name (nur a-z, 0-9, _).", text_color="red")
            return

        if name not in self.favorites:
            self.favorites.append(name)
            self.save_favorites()
            self.update_dropdown()
            self.label_status.configure(text=f"⭐ {name} zu Favoriten hinzugefügt!", text_color="green")
        else:
            self.label_status.configure(text="ℹ️ Streamer ist schon in den Favoriten.", text_color="blue")

    def on_fav_selected(self, choice):
        if choice != "-- Favoriten wählen --":
            self.entry_streamer.delete(0, ctk.END)
            self.entry_streamer.insert(0, choice)
            self.label_status.configure(text=f"Ausgewählt: {choice}", text_color="gray")

    def handle_login(self):
        success, message = self.twitch.start_login(self.on_login_success)
        color = "blue" if success else "red"
        self.label_status.configure(text=message, text_color=color)

    def on_login_success(self):
        self.after(0, lambda: self.btn_login.configure(text="✅ Eingeloggt (Neu einloggen)", fg_color="#2b2b2b"))
        self.after(0, lambda: self.label_status.configure(text="🎉 Erfolgreich mit Twitch eingeloggt!", text_color="green"))

    def on_raid_click(self, event=None):
        streamer_name = self.entry_streamer.get().strip().lower()
        if not streamer_name:
            self.label_status.configure(text="❌ Bitte gib einen Namen ein!", text_color="orange")
            return

        # Input-Validierung per Regex (Zulässig: a-z, 0-9, Unterstrich, max. 25 Zeichen)
        if not re.match(r"^\w{1,25}$", streamer_name):
            self.label_status.configure(text="❌ Ungültiger Streamer-Name (ungültige Zeichen).", text_color="red")
            return

        self.label_status.configure(text=f"🚀 Suche User-ID von {streamer_name}...", text_color="blue")

        def run():
            success, message = self.twitch.execute_raid(streamer_name)
            color = "green" if success else "red"
            self.after(0, lambda: self.label_status.configure(text=message, text_color=color))

        threading.Thread(target=run, daemon=True).start()

if __name__ == "__main__":
    app = TwitchRaidApp()
    app.mainloop()