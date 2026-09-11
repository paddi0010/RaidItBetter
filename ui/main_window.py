import os
import re
import threading
import webbrowser
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from database import get_favorites_db, add_favorite_db, remove_favorite_db, add_raid_history_db, get_raid_history_db, get_last_raid_for_channel
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
        
        try:
            import ctypes
            ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("Paddi.RaidItBetter.v0.4.1")
        except Exception:
            pass

        self.load_token = 0
        
        self.show_only_online = False
        self.last_streamer_data = []

        self.lang = lang
        self.t = load_translations(lang)
        self.twitch = TwitchClient()
        
        self.title("RaidItBetter - v0.4.1-alpha")
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
            self.iconbitmap("assets/icon_task.ico")

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
        
        self.entry_streamer.bind("<Return>", lambda event: self.add_favorite())
        
        self.select_streamer_name = None

        self.btn_add_fav = ctk.CTkButton(self.input_frame, text=self.t.get("save_fav"), fg_color="#333333", hover_color="#444444", width=115, height=35, command=self.add_favorite)
        self.btn_add_fav.pack(side="right")
        
        self.show_only_online = False
        
        # Online Filter
        self.filter_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=20, pady=(5,0))
        
        self.switch_online_filter = ctk.CTkSwitch(
            self.filter_frame,
            text=self.t.get("only_online", "Nur Online Kanäle"),
            font=ctk.CTkFont(size=11),
            command=self.toggle_online_filter
        )
        self.switch_online_filter.pack(side="right")

        self.favorites_frame = ctk.CTkScrollableFrame(self, width=460, height=290, fg_color=("gray92", "gray17"))
        self.favorites_frame.pack(pady=10, padx=20)

        # Raid Button
        self.is_raiding = False
        self.raid_thread = None
        self.btn_raid = ctk.CTkButton(self, text=self.t.get("start_raid"), fg_color="#e91916", hover_color="#c81310", width=460, height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.on_raid_click)
        self.btn_raid.pack(pady=5)

        # Status Label
        self.label_status = ctk.CTkLabel(self, text=self.t.get("ready"), text_color="gray", font=ctk.CTkFont(size=12))
        self.label_status.pack(pady=(0, 10))

        self.refresh_favorites_list()
        threading.Thread(target=self.check_app_updates_background, daemon=True).start()
        threading.Thread(target=self.validate_token_on_startup, daemon=True).start()
        
        self.start_auto_refresh()

    def check_app_updates_background(self):
        import time
        while True:
            has_update, self.latest_release_url = check_update_status()
            color = BTN_ORANGE if has_update else (BTN_GREEN if self.latest_release_url else BTN_GRAY)
            self.after(0, lambda c=color: self.btn_update.configure(fg_color=c))
            time.sleep(1800)
            
    def validate_token_on_startup(self):
        is_valid = self.twitch.validate_and_refresh_if_needed()
        if not is_valid and self.twitch.access_token:
            
            self.after(0, lambda: self.twitch.logout())
            self.after(0, lambda: self.btn_login.configure(text=self.t.get("login"), fg_color="#9146FF", hover_color="#772ce8"))
            self.after(0, lambda: self.label_status.configure(text="❌ Session expired. Please log in again.", text_color="orange"))
        elif is_valid:
            self.after(0, lambda: self.btn_login.configure(text=self.t.get("logout"), fg_color="#d9534f", hover_color="#c9302c"))

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
        
    def toggle_online_filter(self):
        self.show_only_online = self.switch_online_filter.get()
        
        if hasattr(self, "last_streamer_data") and self.last_streamer_data:
            self._render_favorites_ui(self.last_streamer_data)
        else:
            self._render_favorites_ui()
        
    def update_ui(streamers_data):
        for streamer in streamers_data:
            print(f"Streamer: {streamer['name']}, Online: {streamer['is_online']}")

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
        
        self.switch_online_filter.configure(text=self.t.get("only_online", "Nur Online Kanäle"))
        
        lang_text = "🇩🇪 DE" if self.lang == "de" else "🇬🇧 EN"
        self.btn_lang.configure(text=lang_text)

    def refresh_favorites_list(self):
        self.load_token += 1
        current_token = self.load_token
        
        favorites = get_favorites_db()
        if not favorites:
            for widget in self.favorites_frame.winfo_children():
                try: widget.destroy() 
                except Exception: pass
            lbl = ctk.CTkLabel(self.favorites_frame, text=self.t.get("select_fav", "No favourites saved"), text_color="gray")
            lbl.pack(pady=20)
            return

        threading.Thread(target=self.load_favorites_data, args=(favorites, current_token), daemon=True).start()
        
    def start_auto_refresh(self):
        def background_refresh():
            favorites = get_favorites_db()
            if favorites:
                streamers_data = self.twitch.get_streamers_info(favorites)
            
                self.after(0, lambda: self._render_favorites_ui(streamers_data))
            
        threading.Thread(target=background_refresh, daemon=True).start()
        
        self.auto_refresh_timer = self.after(60000, self.start_auto_refresh)

    def load_favorites_data(self, favorites, token):
        try:
            streamer_data = self.twitch.get_streamers_info(favorites)
            self.after(0, lambda: self._safe_render(streamer_data, token))
        except Exception as e:
            print(f"ERROR while loading favorites: {e}")

    def _safe_render(self, streamer_data, token):
        if token != self.load_token:
            return
        self.last_streamer_data = streamer_data
        try:
            self._render_favorites_ui(streamer_data)
        except Exception as e:
            print(f"Render error: {e}")

    def _render_favorites_ui(self, streamer_data=None):
        
        for widget in self.favorites_frame.winfo_children():
                widget.destroy()
            
        if getattr(self, "show_only_online", False):
            display_data = [d for d in streamer_data if d["is_online"]]
        else:
            display_data = streamer_data
            
        if not display_data:
            lbl = ctk.CTkLabel(
                self.favorites_frame, 
                text=self.t.get("no_online_favs", "Keine Online-Kanäle gefunden") 
                if getattr(self, "show_only_online", False) 
                else self.t.get("select_fav", "No favourites saved"), 
                text_color="gray"
            )
            lbl.pack(pady=20)
            return

        for data in display_data:
            print(f"DEBUG Streamer: {data['name']} -> Online: {data['is_online']}, Game: {data.get('game_name')}")
            is_selected = (data["name"].lower() == str(self.select_streamer_name).lower())
            
            border_width = 2 if is_selected else 0
            border_color = "#1f6aa5" if is_selected else None
            
            card = ctk.CTkFrame(
                self.favorites_frame, 
                fg_color=("white", "gray22"), 
                corner_radius=6,
                border_width=border_width,
                border_color=border_color
            )
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
                last_time = get_last_raid_for_channel(data['name'])
                if not last_time:
                    last_time = self.t.get("never")
                details = self.t.get("last_raided", "Last Raid: {date}").format(date=last_time)
                
            lbl_details = ctk.CTkLabel(info_frame, text=details, font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
            lbl_details.pack(fill="x")
            lbl_details.bind("<Button-1>", lambda e, name=data["name"]: self.select_streamer(name))

            btn_del = ctk.CTkButton(card, text="✕", width=25, height=25, fg_color="transparent", hover_color="#d9534f", text_color="gray", command=lambda n=data["name"]: self.remove_favorite(n))
            btn_del.pack(side="right", padx=8)

    def select_streamer(self, name):
        try:
            self.select_streamer_name = name
    
            if hasattr(self, "last_streamer_data") and self.last_streamer_data:
                self._render_favorites_ui(self.last_streamer_data)
        except Exception as e:
            print(f"Error occurred while selecting streamer: {e}")
        
    def load_streamers_async(self, usernames):
        def background_worker():
            streamers_data = self.twitch.get_streamers_info(usernames)
            self.after(0, lambda: self._render_favorites_ui(streamers_data))
        threading.Thread(target=background_worker, daemon=True).start()

    def add_favorite(self):
        streamer_name = self.entry_streamer.get().strip().lower()
        if not streamer_name:
            return
        if not re.match(r"^\w{1,25}$", streamer_name):
            self.label_status.configure(text=self.t.get("invalid_name"), text_color="red")
            return

        if add_favorite_db(streamer_name):
            threading.Thread(target=self.refresh_favorites_list, daemon=True).start()
            msg = self.t.get("fav_added").format(name=streamer_name)
            self.label_status.configure(text=msg, text_color="green")
        else:
            self.label_status.configure(text=self.t.get("fav_exists"), text_color="blue")

    def remove_favorite(self, name):
        remove_favorite_db(name)
        self.refresh_favorites_list()
        msg = self.t.get("fav_removed", "Favourite {name} removed").format(name=name)
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
        if not self.is_raiding:
            streamer_name = self.entry_streamer.get().strip().lower()
            if not streamer_name and hasattr(self, "select_streamer_name") and self.select_streamer_name:
                streamer_name = self.select_streamer_name.strip().lower()
                
            if not streamer_name:
                self.label_status.configure(text=self.t.get("enter_name_raid"), text_color="orange")
                return

            if not re.match(r"^\w{1,25}$", streamer_name):
                self.label_status.configure(text=self.t.get("invalid_streamer"), text_color="red")
                return

            self.is_raiding = True
            self.raid_cancelled = False
            self.btn_raid.configure(text="Abort Raid", fg_color="#333333", hover_color="#444444")

            searching_msg = self.t.get("searching").format(name=streamer_name)
            self.label_status.configure(text=searching_msg, text_color="blue")

            def run():
                success, message = self.twitch.execute_raid(streamer_name)
                
                if not success:
                    if self.raid_cancelled:
                        return
                    self.after(0, lambda: self.reset_raid_button_state())
                    self.after(0, lambda: self.label_status.configure(text=message, text_color="red"))
                    return

                try:
                    add_raid_history_db(streamer_name, viewer_count=0, status="Success")
                    self.after(0, lambda: self.refresh_favorites_list())
                except Exception as e:
                    print(f"Error adding raid history: {e}")

                self.after(0, lambda: self.label_status.configure(text=message, text_color="green"))

                def auto_reset():
                    if self.is_raiding and not self.raid_cancelled:
                        self.is_raiding = False
                        self.reset_raid_button_state()
                        self.label_status.configure(text="⏱️ Raid-Time expired.", text_color="gray")

                self.after(90000, auto_reset)

            self.raid_thread = threading.Thread(target=run, daemon=True)
            self.raid_thread.start()
        else:
            self.raid_cancelled = True
            self.is_raiding = False
            
            def cancel_worker():
                success, message = self.twitch.cancel_raid()
                color = "green" if success else "orange"
                self.after(0, lambda: self.label_status.configure(text=message, text_color=color))
                self.after(0, lambda: self.reset_raid_button_state())

            threading.Thread(target=cancel_worker, daemon=True).start()

    def reset_raid_button_state(self):
        self.is_raiding = False
        self.btn_raid.configure(text=self.t.get("start_raid"), fg_color="#e91916", hover_color="#c81310")

    def report_callback_exception(self, exc, val, tb):
        if "invalid command name" in str(val):
            return
        import traceback
        traceback.print_exception(exc, val, tb)
