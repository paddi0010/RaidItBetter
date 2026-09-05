import os
import re
import threading
import webbrowser
import customtkinter as ctk
from PIL import Image, ImageTk
from database import get_favorites_db, add_favorite_db, remove_favorite_db
from settings import load_language, save_language, load_translations
from twitch_api import TwitchClient
from updater import check_for_updates, check_update_status
from ui.styles import BTN_GREEN, BTN_ORANGE, BTN_GRAY

class LanguageSelectDialog(ctk.CTk):
    def __init__(self, lang=None):
        super().__init__()
        self.title("RaidItBetter - Sprachauswahl / Language")
        self.geometry("320x220")
        self.resizable(False, False)

        self.label = ctk.CTkLabel(self, text="Bitte Sprache wählen\nPlease select language", font=ctk.CTkFont(size=14, weight="bold"))
        self.label.pack(pady=(25, 15))

        self.btn_de = ctk.CTkButton(self, text="🇩🇪 Deutsch", fg_color=BTN_ORANGE, hover_color=BTN_GREEN, width=220, height=40, command=lambda: self.select("de"))
        self.btn_de.pack(pady=5)

        self.btn_en = ctk.CTkButton(self, text="🇬🇧 English", fg_color="#333333", hover_color="#444444", width=220, height=40, command=lambda: self.select("en"))
        self.btn_en.pack(pady=5)

    def select(self, lang):
        save_language(lang)
        self.destroy()

class TwitchRaidApp(ctk.CTk):
    def __init__(self, lang):
        super().__init__()

        self.lang = lang
        self.t = load_translations(lang)
        self.twitch = TwitchClient()

        self.title("RaidItBetter - v0.2.1-alpha")
        self.geometry("520x620")
        self.resizable(False, False)

        self.update_idletasks()
        width = 520
        height = 620
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        if os.path.exists("assets/icon.ico"):
            self.iconbitmap("assets/icon.ico")

        # Header
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5), fill="x", padx=20)

        self.title_label = ctk.CTkLabel(self.header_frame, text=self.t.get("title", "⚡ RaidItBetter"), font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left")

        lang_text = "🇩🇪 DE" if self.lang == "de" else "🇬🇧 EN"
        self.btn_lang = ctk.CTkButton(
            self.header_frame, text=lang_text, width=65, height=28,
            corner_radius=14,
            border_width=1,
            border_color=("gray70", "gray40"),
            fg_color="transparent",
            hover_color=("gray85", "gray25"),
            text_color=("gray20", "gray80"),
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.toggle_language
        )
        self.btn_lang.pack(side="right", padx=(5, 0))

        self.btn_update = ctk.CTkButton(
            self.header_frame, text="🔄", width=32, height=32, 
            fg_color=BTN_GRAY, hover_color=("gray75", "gray35"), 
            font=ctk.CTkFont(size=14), command=self.on_update_click
        )
        self.btn_update.pack(side="right", padx=(0, 5))

        # Login Button
        login_text = self.t.get("logout") if self.twitch.access_token else self.t.get("login")
        login_color = "#d9534f" if self.twitch.access_token else "#9146FF"
        login_hover = "#c9302c" if self.twitch.access_token else "#772ce8"
        
        self.btn_login = ctk.CTkButton(self, text=login_text, fg_color=login_color, hover_color=login_hover, width=460, height=35, command=self.handle_auth_click)
        self.btn_login.pack(pady=5)

        self.input_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.input_frame.pack(pady=5, fill="x", padx=20)

        self.entry_streamer = ctk.CTkEntry(self.input_frame, placeholder_text=self.t.get("placeholder"), width=335, height=35)
        self.entry_streamer.pack(side="left")

        self.btn_add_fav = ctk.CTkButton(self.input_frame, text=self.t.get("save_fav"), fg_color="#333333", hover_color="#444444", width=115, height=35, command=self.add_favorite)
        self.btn_add_fav.pack(side="right")

        self.favorites_frame = ctk.CTkScrollableFrame(self, width=460, height=290, fg_color=("gray92", "gray17"))
        self.favorites_frame.pack(pady=10, padx=20)

        # Raid Button
        self.btn_raid = ctk.CTkButton(self, text=self.t.get("start_raid"), fg_color="#e91916", hover_color="#c81310", width=460, height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.on_raid_click)
        self.btn_raid.pack(pady=5)

        # Status Label
        self.label_status = ctk.CTkLabel(self, text=self.t.get("ready"), text_color="gray", font=ctk.CTkFont(size=12))
        self.label_status.pack(pady=(0, 10))

        self.refresh_favorites_list()
        threading.Thread(target=self.check_app_updates_background, daemon=True).start()

    def check_app_updates_background(self):
        import time
        while True:
            has_update, self.latest_release_url = check_update_status()
            color = BTN_ORANGE if has_update else (BTN_GREEN if self.latest_release_url else BTN_GRAY)
            self.after(0, lambda c=color: self.btn_update.configure(fg_color=c))
            time.sleep(1800)

    def on_update_click(self):
        has_update, self.latest_release_url = check_update_status()
        color = BTN_ORANGE if has_update else (BTN_GREEN if self.latest_release_url else BTN_GRAY)
        self.btn_update.configure(fg_color=color)
        check_for_updates(parent_window=self, silent=False)
        
    def change_language(self, lang):
        self.lang = lang
        save_language(self.lang)
        self.t = load_translations(lang)
        self.update_ui_texts()
        self.refresh_favorites_list()

    def toggle_language(self):
        new_lang = "en" if self.lang == "de" else "de"
        self.change_language(new_lang)

    def update_ui_texts(self):
        self.title_label.configure(text=self.t.get("title", "⚡ RaidItBetter"))
        login_text = self.t.get("logout") if self.twitch.access_token else self.t.get("login")
        login_color = "#d9534f" if self.twitch.access_token else "#9146FF"
        login_hover = "#c9302c" if self.twitch.access_token else "#772ce8"
        self.btn_login.configure(text=login_text, fg_color=login_color, hover_color=login_hover)
        self.entry_streamer.configure(placeholder_text=self.t.get("placeholder"))
        self.btn_add_fav.configure(text=self.t.get("save_fav"))
        self.btn_raid.configure(text=self.t.get("start_raid"))
        self.label_status.configure(text=self.t.get("ready"))
        
        lang_text = "🇩🇪 DE" if self.lang == "de" else "🇬🇧 EN"
        self.btn_lang.configure(text=lang_text)

    def refresh_favorites_list(self):
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()

        favorites = get_favorites_db()
        if not favorites:
            lbl = ctk.CTkLabel(self.favorites_frame, text=self.t.get("select_fav", "Keine Favoriten gespeichert"), text_color="gray")
            lbl.pack(pady=20)
            return

        threading.Thread(target=self._load_favorites_data, args=(favorites,), daemon=True).start()

    def _load_favorites_data(self, favorites):
        try:
            streamer_data = self.twitch.get_streamers_info(favorites)
            self.after(0, lambda: self._render_favorites_ui(streamer_data))
        except Exception as e:
            print(f"FEHLER beim Laden der Favoriten: {e}")

    def _render_favorites_ui(self, streamer_data):
        for widget in self.favorites_frame.winfo_children():
            widget.destroy()

        for data in streamer_data:
            card = ctk.CTkFrame(self.favorites_frame, fg_color=("white", "gray22"), corner_radius=6)
            card.pack(pady=4, fill="x", padx=5)

            card.bind("<Button-1>", lambda e, name=data["name"]: self.select_streamer(name))

            dot_color = "green" if data["is_online"] else "gray"
            lbl_dot = ctk.CTkLabel(card, text="●", text_color=dot_color, font=ctk.CTkFont(size=14))
            lbl_dot.pack(side="left", padx=(10, 6))
            lbl_dot.bind("<Button-1>", lambda e, name=data["name"]: self.select_streamer(name))

            info_frame = ctk.CTkFrame(card, fg_color="transparent")
            info_frame.pack(side="left", fill="both", expand=True, pady=8, padx=5)
            info_frame.bind("<Button-1>", lambda e, name=data["name"]: self.select_streamer(name))

            status_text = self.t.get("online") if data["is_online"] else self.t.get("offline")
            name_text = f"{data['name']} ({status_text})"
            lbl_name = ctk.CTkLabel(info_frame, text=name_text, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
            lbl_name.pack(fill="x")
            lbl_name.bind("<Button-1>", lambda e, name=data["name"]: self.select_streamer(name))

            if data["is_online"]:
                details = data['game_name']
            else:
                last_time = data['last_raided'] if data['last_raided'] else self.t.get("never")
                details = self.t.get("last_raided", "Letzter Raid: {date}").format(date=last_time)

            lbl_details = ctk.CTkLabel(info_frame, text=details, font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
            lbl_details.pack(fill="x")
            lbl_details.bind("<Button-1>", lambda e, name=data["name"]: self.select_streamer(name))

            btn_del = ctk.CTkButton(card, text="✕", width=25, height=25, fg_color="transparent", hover_color="#d9534f", text_color="gray", command=lambda n=data["name"]: self.remove_favorite(n))
            btn_del.pack(side="right", padx=8)

    def select_streamer(self, name):
        self.entry_streamer.delete(0, ctk.END)
        self.entry_streamer.insert(0, name)

    def add_favorite(self):
        name = self.entry_streamer.get().strip().lower()
        if not name:
            self.label_status.configure(text=self.t.get("enter_name_save"), text_color="orange")
            return
        if not re.match(r"^\w{1,25}$", name):
            self.label_status.configure(text=self.t.get("invalid_name"), text_color="red")
            return

        if add_favorite_db(name):
            self.refresh_favorites_list()
            msg = self.t.get("fav_added").format(name=name)
            self.label_status.configure(text=msg, text_color="green")
        else:
            self.label_status.configure(text=self.t.get("fav_exists"), text_color="blue")

    def remove_favorite(self, name):
        remove_favorite_db(name)
        self.refresh_favorites_list()
        msg = self.t.get("fav_removed", "Favorit {name} entfernt").format(name=name)
        self.label_status.configure(text=msg, text_color="blue")

    def handle_auth_click(self):
        if self.twitch.access_token:
            self.twitch.logout()
            self.btn_login.configure(text=self.t.get("login"), fg_color="#9146FF", hover_color="#772ce8")
            self.label_status.configure(text=self.t.get("logged_out"), text_color="blue")
        else:
            success, message = self.twitch.start_login(self.on_login_success)
            color = "blue" if success else "red"
            self.label_status.configure(text=message, text_color=color)

    def on_login_success(self, event=None):
        self.after(0, lambda: self.btn_login.configure(text=self.t.get("logout"), fg_color="#d9534f", hover_color="#c9302c"))
        self.after(0, lambda: self.label_status.configure(text=self.t.get("login_success"), text_color="green"))
        self.refresh_favorites_list()

    def on_raid_click(self, event=None):
        streamer_name = self.entry_streamer.get().strip().lower()
        if not streamer_name:
            self.label_status.configure(text=self.t.get("enter_name_raid"), text_color="orange")
            return

        if not re.match(r"^\w{1,25}$", streamer_name):
            self.label_status.configure(text=self.t.get("invalid_streamer"), text_color="red")
            return

        searching_msg = self.t.get("searching").format(name=streamer_name)
        self.label_status.configure(text=searching_msg, text_color="blue")

        def run():
            success, message = self.twitch.execute_raid(streamer_name)
            color = "green" if success else "red"
            self.after(0, lambda: self.label_status.configure(text=message, text_color=color))
            self.after(0, self.refresh_favorites_list)

        threading.Thread(target=run, daemon=True).start()