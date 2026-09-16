import os
import re
import threading
import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
from services.database import get_favorites_db, add_favorite_db, remove_favorite_db, add_raid_history_db, get_last_raid_for_channel
from core.settings import save_language, load_translations
from api.twitch_api import TwitchClient
from ui.components import StreamerCard
from ui.settings_window import SettingsPanel
from services.updater import check_for_updates, check_update_status
from ui.styles import ( COLOR_PRIMARY, COLOR_PRIMARY_HOVER, COLOR_DANGER, COLOR_DANGER_HOVER, COLOR_RAID, COLOR_RAID_HOVER, BTN_GREEN, BTN_ORANGE, BTN_GRAY, BTN_GRAY_HOVER, BG_CARD, BG_SCROLL )
from ui.history_window import RaidHistoryWindow
from ui.about_window import Aboutwindow
from core.settings import APP_VERSION

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
        
        self.title(f"RaidItBetter - {APP_VERSION}")
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

        self.main_content_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.main_content_frame.pack(side="left", fill="both", expand=True)

        # Header
        self.header_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.header_frame.pack(pady=(15, 5), fill="x", padx=20)

        self.title_label = ctk.CTkLabel(self.header_frame, text=self.t.get("title", "⚡ RaidItBetter"), font=ctk.CTkFont(size=20, weight="bold"))
        self.title_label.pack(side="left")

        # Update Button
        self.btn_update = ctk.CTkButton(
            self.header_frame, text="🔄", width=32, height=32, 
            fg_color=BTN_GRAY, hover_color=("gray75", "gray35"), 
            font=ctk.CTkFont(size=14), command=self.on_update_click
        )
        self.btn_update.pack(side="right", padx=(0, 5))
        self.btn_update.bind("<Enter>", lambda e: self.label_status.configure(text=self.t.get("tooltip_update", "Check for updates")))
        self.btn_update.bind("<Leave>", lambda e: self.label_status.configure(text=self.t.get("ready")))
        
        # About Button
        self.btn_about = ctk.CTkButton(
            self.header_frame, text="ℹ️", width=32, height=32,
            fg_color=BTN_GRAY, hover_color=BTN_GRAY_HOVER,
            font=ctk.CTkFont(size=14), command=self.open_about_window
        )
        self.btn_about.pack(side="right", padx=(0, 5))
        self.btn_about.bind("<Enter>", lambda e: self.label_status.configure(text=self.t.get("tooltip_about", "About")))
        self.btn_about.bind("<Leave>", lambda e: self.label_status.configure(text=self.t.get("ready")))
        
        # Settings Button
        self.btn_settings = ctk.CTkButton(
            self.header_frame, text="⚙️", width=32, height=32,
            fg_color=BTN_GRAY, hover_color=BTN_GRAY_HOVER,
            font=ctk.CTkFont(size=14), command=self.toggle_settings
        )
        self.btn_settings.pack(side="right", padx=(0, 5))
        self.btn_settings.bind("<Enter>", lambda e: self.label_status.configure(text=self.t.get("tooltip_settings", "Settings")))
        self.btn_settings.bind("<Leave>", lambda e: self.label_status.configure(text=self.t.get("ready")))
        
        # Raid History Button
        self.btn_history = ctk.CTkButton(
            self.header_frame, text="🧾", width=32, height=32,
            fg_color=BTN_GRAY, hover_color=("gray75", "gray35"),
            font=ctk.CTkFont(size=14), command=self.open_history_window
        )
        self.btn_history.pack(side="right", padx=(0, 5))
        self.btn_history.bind("<Enter>", lambda e: self.label_status.configure(text=self.t.get("tooltip_history", "History")))
        self.btn_history.bind("<Leave>", lambda e: self.label_status.configure(text=self.t.get("ready")))

        # Login Button
        login_text = self.t.get("logout") if self.twitch.access_token else self.t.get("login")
        login_color = COLOR_DANGER if self.twitch.access_token else COLOR_PRIMARY
        login_hover = COLOR_DANGER_HOVER if self.twitch.access_token else COLOR_PRIMARY_HOVER
        
        self.btn_login = ctk.CTkButton(self.main_content_frame, text=login_text, fg_color=login_color, hover_color=login_hover, width=460, height=35, command=self.handle_auth_click)
        self.btn_login.pack(pady=5)

        self.input_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.input_frame.pack(pady=5, fill="x", padx=20)

        self.entry_streamer = ctk.CTkEntry(self.input_frame, placeholder_text=self.t.get("placeholder"), width=335, height=35)
        self.entry_streamer.pack(side="left")
        self.entry_streamer.bind("<Return>", lambda event: self.add_favorite())
        
        self.select_streamer_name = None

        self.btn_add_fav = ctk.CTkButton(self.input_frame, text=self.t.get("save_fav"), fg_color="#333333", hover_color="#444444", width=115, height=35, command=self.add_favorite)
        self.btn_add_fav.pack(side="right")
        
        # Online Filter
        self.filter_frame = ctk.CTkFrame(self.main_content_frame, fg_color="transparent")
        self.filter_frame.pack(fill="x", padx=20, pady=(5,0))
        
        self.switch_online_filter = ctk.CTkSwitch(
            self.filter_frame,
            text=self.t.get("only_online", "Nur Online Kanäle"),
            font=ctk.CTkFont(size=11),
            command=self.toggle_online_filter
        )
        self.switch_online_filter.pack(side="right")

        self.favorites_frame = ctk.CTkScrollableFrame(self.main_content_frame, width=460, height=290, fg_color=BG_SCROLL)
        self.favorites_frame.pack(pady=10, padx=20)

        # Raid Button
        self.is_raiding = False
        self.raid_thread = None
        self.btn_raid = ctk.CTkButton(self.main_content_frame, text=self.t.get("start_raid"), fg_color=COLOR_RAID, hover_color=COLOR_RAID_HOVER, width=460, height=40, font=ctk.CTkFont(size=14, weight="bold"), command=self.on_raid_click)
        self.btn_raid.pack(pady=5)

        # Status Label
        self.label_status = ctk.CTkLabel(self.main_content_frame, text=self.t.get("ready"), text_color="gray", font=ctk.CTkFont(size=12))
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
        
        if hasattr(self, "history_win_ref") and self.history_win_ref:
            try:
                self.history_win_ref.destroy()
            except Exception:
                pass
            self.history_win_ref = None

    def toggle_language(self):
        new_lang = "en" if self.lang == "de" else "de"
        self.change_language(new_lang)
        
    def toggle_online_filter(self):
        self.show_only_online = self.switch_online_filter.get()
        if hasattr(self, "last_streamer_data") and self.last_streamer_data:
            current_favs = [f.lower() for f in get_favorites_db()]
            valid_data = [d for d in self.last_streamer_data if d["name"].lower() in current_favs]
            self._render_favorites_ui(valid_data)
        else:
            self.refresh_favorites_list()
            
    def toggle_settings(self):
        if getattr(self, "settings_open", False):
            if hasattr(self, "settings_frame") and self.settings_frame:
                self.settings_frame.destroy()
                del self.settings_frame
            self.geometry("520x620")
            self.settings_open = False
        else:
            self.geometry("920x620")
            self.setup_settings_panel()
            self.settings_open = True

    def setup_settings_panel(self):
        self.settings_frame = SettingsPanel(self, self)
        self.settings_frame.pack(side="right", fill="both", expand=False)

    def on_settings_language_change(self, choice):
        lang_code = "de" if choice == "Deutsch" else "en"
        if hasattr(self, "change_language"):
            self.change_language(lang_code)

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

        display_data = sorted(display_data, key=lambda x: (not x["is_online"], x["name"].lower()))
            
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
            is_selected = (data["name"].lower() == str(self.select_streamer_name).lower())
            
            last_time = None
            if not data["is_online"]:
                last_time = get_last_raid_for_channel(data['name'])

            StreamerCard(
                parent=self.favorites_frame,
                data=data,
                is_selected=is_selected,
                on_click=self.select_streamer,
                on_delete=self.remove_favorite,
                translations=self.t,
                last_raid_time=last_time
            )

    def select_streamer(self, name):
        try:
            self.select_streamer_name = name
            if hasattr(self, "last_streamer_data") and self.last_streamer_data:
                self._render_favorites_ui(self.last_streamer_data)
        except Exception as e:
            print(f"Error occurred while selecting streamer: {e}")

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
        if hasattr(self, "last_streamer_data") and self.last_streamer_data:
            self.last_streamer_data = [d for d in self.last_streamer_data if d["name"].lower() != name.lower()]

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
                try:
                    success, message = self.twitch.execute_raid(streamer_name)
                    if not success:
                        if self.raid_cancelled:
                            return
                        self.after(0, lambda: self.reset_raid_button_state())
                        self.after(0, lambda: self.label_status.configure(text=message, text_color="red"))
                        return

                    add_raid_history_db(streamer_name, viewer_count=0, status="Success")
                    self.after(0, lambda: self.refresh_favorites_list())
                    self.after(0, lambda: self.label_status.configure(text=message, text_color="green"))
                    
                except Exception as ex:
                    self.after(0, lambda: self.label_status.configure(text=f"Raid-Fehler: {ex}", text_color="red"))
                    self.after(0, lambda: self.reset_raid_button_state())
                self.raid_thread = threading.Thread(target=run, daemon=True)
                self.raid_thread.start()

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

    def open_history_window(self):
        if hasattr(self, "history_win_ref") and self.history_win_ref and self.history_win_ref.winfo_exists():
            self.history_win_ref.focus()
            return
        self.history_win_ref = RaidHistoryWindow(self, self.t)
        
    def open_about_window(self):
        if hasattr(self, "about_win_ref") and self.about_win_ref and self.about_win_ref.winfo_exists():
            self.about_win_ref.focus()
            return
        self.about_win_ref = Aboutwindow(self, self.t)