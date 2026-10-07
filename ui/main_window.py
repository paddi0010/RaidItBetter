import os
import re
import threading
import sys
import time
from PySide6.QtCore import Q_ARG, QMetaObject, QRect, QSize, Qt, QTimer, Signal, Slot, QByteArray, QPoint, QPropertyAnimation, QEasingCurve, QMimeData
from PySide6.QtGui import QDrag, QIcon, QPixmap, QPainter, QPainterPath
from PySide6.QtWidgets import (
    QApplication, QDialog, QListWidget, QListWidgetItem, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QLineEdit, QScrollArea, QFrame, QCheckBox, QComboBox, QMenu, QStackedWidget, QGraphicsOpacityEffect
)
from services.database import (
    get_favorites_db, add_favorite_db, remove_favorite_db, 
    add_raid_history_db, get_last_raid_for_channel, update_favorites_order
)
from core.settings import save_language, load_translations, APP_VERSION
from api.twitch_api import TwitchClient
from ui.settings_window import SettingsPanel
from ui.history_window import RaidHistoryWindow
from ui.about_window import Aboutwindow
from ui.login_window import LoginPanel
from services.updater import check_for_updates, check_update_status

from ui.styles.login_window_style import BTN_LOGIN
from ui.styles.main_window_style import (
    MAIN_WINDOW_STYLE, STREAMER_CARD_STYLE, STREAMER_CARD_DELETE_BTN,
    HEADER_BTN_STYLE, INPUT_CONTAINER_STYLE, ENTRY_STREAMER_STYLE,
    BTN_ADD_FAV_STYLE, SCROLL_AREA_STYLE, BTN_RAID_START, BTN_RAID_CANCEL,
    STATUSBAR_STYLE, PROFILE_MENU, PROGRESS_BAR
)

class LoadingPanel(QWidget):
    def __init__(self, parent=None, translations=None):
        super().__init__(parent)
        self.t = translations or {}
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        self.setStyleSheet("background-color: #0d1117;")
        
        lbl_logo = QLabel("⚡")
        lbl_logo.setStyleSheet("font-size: 40px; background: transparent;")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_logo)
        
        lbl_title = QLabel(self.t.get("loading_title", "RaidItBetter"))
        lbl_title.setStyleSheet("font-size: 20px; font-weight: bold; color: white; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)
        
        lbl_sub = QLabel(self.t.get("loading_sub", "Daten werden geladen..."))
        lbl_sub.setStyleSheet("font-size: 13px; color: #8b949e; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)


class LoginPanel(QFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent)
        self.main_app = main_app
        self.setStyleSheet("background-color: #0d1117;")
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(40, 40, 40, 40)
        layout.setSpacing(20)
        
        layout.addStretch()
        
        title = QLabel("Twitch Login")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; background: transparent;")
        layout.addWidget(title)
        
        lang = getattr(self.main_app, "lang", "de")
        if lang == "en":
            desc_text = "To execute raids and manage your favorites efficiently, logging in with your Twitch account is required."
            btn_text = "Log in with Twitch 🚀"
        else:
            desc_text = "Um Raids auszuführen und deine Favoriten optimal zu verwalten, ist eine Anmeldung mit deinem Twitch-Account erforderlich."
            btn_text = "Mit Twitch anmelden 🚀"

        desc = QLabel(desc_text)
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 14px; color: #8b949e; background: transparent;")
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        btn_login = QPushButton(btn_text)
        btn_login.setFixedHeight(50)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet(BTN_LOGIN)
        btn_login.clicked.connect(self.main_app.handle_auth_click)
        layout.addWidget(btn_login)
        
        layout.addStretch()


class LanguagePanel(QWidget):
    def __init__(self, parent=None, on_next_callback=None):
        super().__init__(parent)
        self.on_next_callback = on_next_callback

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(20)

        lbl_title = QLabel("⚡ Willkommen bei RaidItBetter")
        lbl_title.setStyleSheet("font-size: 22px; font-weight: bold; color: white; background: transparent;")
        lbl_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_title)

        lbl_sub = QLabel("Bitte wähle deine bevorzugte Sprache aus:\nPlease select your language:")
        lbl_sub.setStyleSheet("font-size: 13px; color: #8b949e; background: transparent;")
        lbl_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_sub)

        self.combo_lang = QComboBox()
        self.combo_lang.setFixedWidth(220)
        self.combo_lang.setFixedHeight(35)
        self.combo_lang.setStyleSheet("color: #c9d1d9; background-color: #161b22; border: 1px solid #30363d; border-radius: 6px; padding: 4px 10px; font-size: 13px;")
        self.combo_lang.addItem("🇩🇪 Deutsch", "de")
        self.combo_lang.addItem("🇬🇧 English", "en")
        layout.addWidget(self.combo_lang, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_next = QPushButton("Weiter ➔")
        btn_next.setFixedWidth(220)
        btn_next.setFixedHeight(38)
        btn_next.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_next.setStyleSheet("""
            QPushButton {
                background-color: #238636;
                color: white;
                border-radius: 6px;
                font-weight: bold;
                font-size: 13px;
                border: none;
            }
            QPushButton:hover {
                background-color: #2ea043;
            }
        """)
        btn_next.clicked.connect(self.on_next_click)
        layout.addWidget(btn_next, alignment=Qt.AlignmentFlag.AlignCenter)

    def on_next_click(self):
        selected_lang = self.combo_lang.currentData()
        if self.on_next_callback:
            self.on_next_callback(selected_lang)

class FavoritesListWidget(QListWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(False)


class StreamerCard(QFrame):
    def __init__(self, parent, data, is_selected, on_click, on_delete, on_move_up, on_move_down, translations, last_raid_time, show_arrows=True):
        super().__init__(parent)
        self.on_click_callback = on_click
        self.streamer_name = data["name"]

        border_color = "#9146FF" if is_selected else "#21262d"
        bg_color = "#161b22" if is_selected else "#111418"
       
        self.setStyleSheet(STREAMER_CARD_STYLE.format(bg_color=bg_color, border_color=border_color))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(85)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 10, 12, 10)
        layout.setSpacing(10)

        if show_arrows:
            arrow_layout = QVBoxLayout()
            arrow_layout.setSpacing(2)
            arrow_layout.setContentsMargins(0, 0, 0, 0)
            
            arrow_btn_style = """
                QPushButton {
                    background-color: #21262d;
                    color: #8b949e;
                    border: 1px solid #30363d;
                    border-radius: 3px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #30363d;
                    color: white;
                    border-color: #8b949e;
                }
            """
            
            btn_up = QPushButton("▲")
            btn_up.setFixedSize(22, 22)
            btn_up.setStyleSheet(arrow_btn_style)
            btn_up.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_up.clicked.connect(lambda: on_move_up(self.streamer_name))
            
            btn_down = QPushButton("▼")
            btn_down.setFixedSize(22, 22)
            btn_down.setStyleSheet(arrow_btn_style)
            btn_down.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_down.clicked.connect(lambda: on_move_down(self.streamer_name))
            
            arrow_layout.addWidget(btn_up)
            arrow_layout.addWidget(btn_down)
            layout.addLayout(arrow_layout)

        is_online = data.get("is_online", False)
        lbl_dot = QLabel("🟢" if is_online else "⚪")
        lbl_dot.setStyleSheet("font-size: 8px; background: transparent; border: none;")
        layout.addWidget(lbl_dot, alignment=Qt.AlignmentFlag.AlignTop)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(3)
        info_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_name = QLabel(self.streamer_name)
        self.lbl_name.setStyleSheet("font-size: 13px; font-weight: bold; color: white; background: transparent; border: none;")
        info_layout.addWidget(self.lbl_name)

        last_raided_template = translations.get("last_raided", "Letzter Raid: {date}")
        offline_label_text = translations.get("offline", "Offline")

        if is_online:
            title_text = data.get("title", "")
            self.lbl_title = QLabel(title_text)
            self.lbl_title.setWordWrap(True)
            self.lbl_title.setStyleSheet("font-size: 11px; color: #8b949e; background: transparent; border: none;")
            info_layout.addWidget(self.lbl_title)
            
            if last_raid_time:
                formatted_last_raid = last_raided_template.format(date=last_raid_time)
                self.lbl_last_raid = QLabel(formatted_last_raid)
                self.lbl_last_raid.setStyleSheet("font-size: 10px; color: #6e7681; background: transparent; border: none;")
                info_layout.addWidget(self.lbl_last_raid)
        else:
            if last_raid_time:
                offline_text = last_raided_template.format(date=last_raid_time)
            else:
                offline_text = offline_label_text
            
            self.lbl_offline = QLabel(offline_text)
            self.lbl_offline.setStyleSheet("font-size: 11px; color: #8b949e; background: transparent; border: none;")
            info_layout.addWidget(self.lbl_offline)

        layout.addLayout(info_layout, stretch=1)
        layout.addStretch()

        right_layout = QVBoxLayout()
        right_layout.setSpacing(3)
        right_layout.setContentsMargins(0, 0, 0, 0)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        if is_online:
            game_name = data.get("game_name", "")
            if game_name:
                self.lbl_game = QLabel(game_name)
                self.lbl_game.setStyleSheet("font-size: 11px; color: #8b949e; background: transparent; border: none;")
                self.lbl_game.setAlignment(Qt.AlignmentFlag.AlignRight)
                right_layout.addWidget(self.lbl_game)

            viewer_count = data.get("viewer_count", 0)
            self.lbl_viewers = QLabel(f"👥 {viewer_count}")
            self.lbl_viewers.setStyleSheet("font-size: 11px; font-weight: bold; color: #c9d1d9; background: transparent; border: none;")
            self.lbl_viewers.setAlignment(Qt.AlignmentFlag.AlignRight)
            right_layout.addWidget(self.lbl_viewers)

        layout.addLayout(right_layout)

        btn_del = QPushButton("✕")
        btn_del.setFixedSize(26, 26)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setStyleSheet(STREAMER_CARD_DELETE_BTN)
        btn_del.clicked.connect(lambda: on_delete(data["name"]))
        layout.addWidget(btn_del, alignment=Qt.AlignmentFlag.AlignTop)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.on_click_callback(self.streamer_name)
        super().mousePressEvent(event)


class TwitchRaidApp(QMainWindow):
    data_loaded_signal = Signal(list)
    update_raid_btn_signal = Signal(str, str)
    profile_updated_signal = Signal(object)
    update_status_signal = Signal(bool, str)
    
    show_login_signal = Signal()
    show_main_signal = Signal()
    start_login_signal = Signal()

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
        self.select_streamer_name = None
        self.is_raiding = False
        self.raid_cancelled = False

        self.lang = lang
        self.t = load_translations(lang)
        self.twitch = TwitchClient()

        self.about_open = False
        self.settings_open = False
        self.history_open = False

        self.setWindowTitle(f"RaidItBetter - {APP_VERSION}")
        self.setFixedSize(520, 620)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        self.central_widget = QWidget(self)
        self.setCentralWidget(self.central_widget)
        
        self.main_layout = QHBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(0)

        self.stack = QStackedWidget()
        self.main_layout.addWidget(self.stack)

        self.loading_panel = LoadingPanel(self, self.t)
        self.stack.addWidget(self.loading_panel)

        self.language_panel = LanguagePanel(self, on_next_callback=self.on_language_selected)
        self.stack.addWidget(self.language_panel)

        self.login_panel = LoginPanel(self, self)
        self.stack.addWidget(self.login_panel)

        self.content_container = QWidget()
        self.content_layout = QVBoxLayout(self.content_container)
        self.content_layout.setContentsMargins(20, 15, 20, 15)
        self.content_layout.setSpacing(10)
        self.stack.addWidget(self.content_container)

        self.panel_container = QWidget()
        self.panel_container.hide()
        self.panel_container_layout = QVBoxLayout(self.panel_container)
        self.panel_container_layout.setContentsMargins(0, 0, 0, 0)
        self.panel_container_layout.setSpacing(0)
        self.main_layout.addWidget(self.panel_container)

        self.stack.setCurrentWidget(self.loading_panel)
        
        # --- 1. HEADER (Title, Update-Button & Profile) ---
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0, 0, 0, 5)
        header_layout.setSpacing(10)

        self.title_label = QLabel(self.t.get("title", "⚡ RaidItBetter"))
        self.title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: white; background: transparent;")
        header_layout.addWidget(self.title_label)
        header_layout.addStretch()
        
        self.btn_update = QPushButton("🔄 Update")
        self.btn_update.setFixedHeight(34)
        self.btn_update.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_update.setToolTip("Nach Updates suchen")
        self.btn_update.setStyleSheet("""
            QPushButton {
                background-color: #21262d;
                color: #8b949e;
                border: 1px solid #30363d;
                border-radius: 6px;
                padding: 0 10px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #30363d;
                color: white;
                border-color: #8b949e;
            }
        """)
        self.btn_update.clicked.connect(self.on_update_click)
        header_layout.addWidget(self.btn_update)

        self.btn_profile = QPushButton("👤")
        self.btn_profile.setFixedSize(34, 34)
        self.btn_profile.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_profile.setToolTip("Login / Account")
        self.btn_profile.setStyleSheet(HEADER_BTN_STYLE)

        self.profile_menu = QMenu(self)
        self.profile_menu.setStyleSheet(PROFILE_MENU)
        
        self.btn_profile.clicked.connect(self.handle_auth_click)
        header_layout.addWidget(self.btn_profile)

        self.content_layout.addLayout(header_layout)
        
        # --- 2. INPUT CONTAINER ---
        input_container = QFrame()
        input_container.setStyleSheet(INPUT_CONTAINER_STYLE)
        input_layout = QHBoxLayout(input_container)
        input_layout.setContentsMargins(10, 8, 10, 8)

        self.entry_streamer = QLineEdit()
        self.entry_streamer.setPlaceholderText(self.t.get("placeholder", "Streamer Name..."))
        self.entry_streamer.setFixedHeight(35)
        self.entry_streamer.setStyleSheet(ENTRY_STREAMER_STYLE)
        self.entry_streamer.returnPressed.connect(self.add_favorite)
        input_layout.addWidget(self.entry_streamer)

        self.btn_add_fav = QPushButton(self.t.get("save_fav", "Hinzufügen"))
        self.btn_add_fav.setFixedHeight(35)
        self.btn_add_fav.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_add_fav.setStyleSheet(BTN_ADD_FAV_STYLE)
        self.btn_add_fav.clicked.connect(self.add_favorite)
        input_layout.addWidget(self.btn_add_fav)
        self.content_layout.addWidget(input_container)
        
        # --- 3. FILTER & SORT ---
        filter_layout = QHBoxLayout()
        
        self.combo_sort = QComboBox()
        font = self.combo_sort.font()
        font.setPointSize(10)
        self.combo_sort.setFont(font)
        self.combo_sort.setStyleSheet("color: #c9d1d9; background-color: #161b22; border: 1px solid #30363d; border-radius: 4px; padding: 2px 6px;")
        
        self.combo_sort.addItem(self.t.get("sort_custom", "Benutzerdefiniert"), "custom")
        self.combo_sort.addItem(self.t.get("sort_viewers_high", "Viewer: Hoch --> Niedrig"), "high_low")
        self.combo_sort.addItem(self.t.get("sort_viewers_low", "Viewer: Niedrig --> Hoch"), "low_high")
        
        self.combo_sort.currentIndexChanged.connect(self.on_sort_changed)
        filter_layout.addWidget(self.combo_sort)
        
        self.checkbox_online = QCheckBox(self.t.get("only_online", "Nur Online Kanäle"))
        self.checkbox_online.setStyleSheet("color: #c9d1d9; font-size: 11px;")
        self.checkbox_online.stateChanged.connect(self.toggle_online_filter)
        filter_layout.addWidget(self.checkbox_online)
        
        self.content_layout.addLayout(filter_layout)
        
        # --- 4. FAVORITES LIST ---
        self.list_favorites = FavoritesListWidget()
        self.list_favorites.setSelectionMode(QListWidget.SelectionMode.SingleSelection)
        self.list_favorites.setStyleSheet(SCROLL_AREA_STYLE)
        self.content_layout.addWidget(self.list_favorites)
        
        # --- 5. RAID BUTTON ---
        self.btn_raid = QPushButton(self.t.get("start_raid", "⚡ Raid starten"))
        self.btn_raid.setFixedHeight(40)
        self.btn_raid.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_raid.setStyleSheet(BTN_RAID_START)
        self.btn_raid.clicked.connect(self.on_raid_click)
        self.content_layout.addWidget(self.btn_raid)
        
        # --- 6. Bottom Bar (Status left, Tools right) ---
        bottom_bar_layout = QHBoxLayout()
        bottom_bar_layout.setContentsMargins(0, 5, 0, 0)
        bottom_bar_layout.setSpacing(6)
        
        self.label_status = QLabel(self.t.get("ready", "Bereit"))
        self.label_status.setStyleSheet(STATUSBAR_STYLE)
        bottom_bar_layout.addWidget(self.label_status, stretch=1)
        
        self.btn_history = self.create_header_btn("🧾", self.toggle_history, "History")
        self.btn_settings = self.create_header_btn("⚙️", self.toggle_settings, "Settings")
        self.btn_about = self.create_header_btn("ℹ️", self.toggle_about, "About")
                
        bottom_bar_layout.addWidget(self.btn_history)
        bottom_bar_layout.addWidget(self.btn_settings)
        bottom_bar_layout.addWidget(self.btn_about)
        
        self.content_layout.addLayout(bottom_bar_layout)
        
        self.data_loaded_signal.connect(self._render_favorites_ui)
        self.update_raid_btn_signal.connect(self._apply_raid_btn_style)
        self.profile_updated_signal.connect(self._apply_profile_image)
        self.update_status_signal.connect(self.apply_update_button_style)
        
        self.show_login_signal.connect(self.show_login_view)
        self.show_main_signal.connect(self.show_main_view)
        self.start_login_signal.connect(self._perform_auth_in_main_thread)

        threading.Thread(target=self.check_app_updates_background, daemon=True).start()
        threading.Thread(target=self.validate_token_on_startup, daemon=True).start()

        self.auto_timer = QTimer(self)
        self.auto_timer.timeout.connect(self.start_auto_refresh)
        self.auto_timer.start(30000)

        self.token_timer = QTimer(self)
        self.token_timer.timeout.connect(self.background_token_refresh)
        self.token_timer.start(1800000)

    def _open_side_panel(self, panel_widget_class):
        while self.panel_container_layout.count():
            child = self.panel_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        if panel_widget_class == RaidHistoryWindow:
            panel = panel_widget_class(self.panel_container, self.t)
        else:
            panel = panel_widget_class(self.panel_container, self)

        self.panel_container_layout.addWidget(panel)
        self.panel_container.show()
        self.setFixedSize(920, 620)

    def _close_side_panel(self):
        while self.panel_container_layout.count():
            child = self.panel_container_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        self.panel_container.hide()
        self.setFixedSize(520, 620)

    def toggle_settings(self):
        if self.settings_open:
            self._close_side_panel()
            self.settings_open = False
        else:
            self.about_open = False
            self.history_open = False
            self._open_side_panel(SettingsPanel)
            self.settings_open = True

    def toggle_about(self):
        if self.about_open:
            self._close_side_panel()
            self.about_open = False
        else:
            self.settings_open = False
            self.history_open = False
            self._open_side_panel(Aboutwindow)
            self.about_open = True
            
    def toggle_history(self):
        if self.history_open:
            self._close_side_panel()
            self.history_open = False
        else:
            self.settings_open = False
            self.about_open = False
            self._open_side_panel(RaidHistoryWindow)
            self.history_open = True

    def background_token_refresh(self):
        if self.twitch.access_token:
            threading.Thread(target=self.twitch.validate_and_refresh_if_needed, daemon=True).start()

    def switch_view_animated(self, target_widget):
        effect = QGraphicsOpacityEffect(target_widget)
        target_widget.setGraphicsEffect(effect)
        
        self.stack.setCurrentWidget(target_widget)
        
        self.fade_anim = QPropertyAnimation(effect, b"opacity")
        self.fade_anim.setDuration(350)
        self.fade_anim.setStartValue(0.0)
        self.fade_anim.setEndValue(1.0)
        self.fade_anim.setEasingCurve(QEasingCurve.Type.InOutQuad)
        self.fade_anim.start()

    @Slot()
    def show_login_view(self):
        self.switch_view_animated(self.login_panel)

    @Slot()
    def show_main_view(self):
        self.switch_view_animated(self.content_container)
        self.refresh_favorites_list()
        self.update_profile_button()

    def create_header_btn(self, text, callback, tooltip):
        btn = QPushButton(text)
        btn.setFixedSize(32, 32)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        btn.setToolTip(tooltip)
        btn.setStyleSheet(HEADER_BTN_STYLE)
        btn.clicked.connect(callback)
        return btn

    def check_app_updates_background(self):
        while True:
            has_update, url = check_update_status()
            
            # --- ZUM TESTEN (Erzwungen auf True): ---
            # has_update = True
            # url = "https://github.com"
            # ----------------------------------------
            
            self.update_status_signal.emit(has_update, url)
            break
            
        time.sleep(1800)

    @Slot(bool, str)
    def apply_update_button_style(self, has_update, url):
        self.latest_release_url = url
        if has_update:
            style = """
                QPushButton {
                    background-color: #9146FF !important;
                    color: white !important;
                    border: none !important;
                    border-radius: 6px;
                    padding: 0 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #772ce8 !important;
                }
            """
            self.btn_update.setStyleSheet(style)
            self.btn_update.setText("🚀 Update verfügbar")
        else:
            default_style = """
                QPushButton {
                    background-color: #21262d !important;
                    color: #8b949e !important;
                    border: 1px solid #30363d !important;
                    border-radius: 6px;
                    padding: 0 10px;
                    font-size: 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #30363d !important;
                    color: white !important;
                    border-color: #8b949e !important;
                }
            """
            self.btn_update.setStyleSheet(default_style)
            self.btn_update.setText("🔄 Update")
            
        self.btn_update.update()

    def validate_token_on_startup(self):
        def background_validate():
            time.sleep(1.5)
            favorites = get_favorites_db()
            if favorites and self.twitch.access_token:
                try:
                    self.last_streamer_data = self.twitch.get_streamers_info(favorites)
                except Exception as e:
                    print(f"[ERROR] Fehler beim Vorab-Laden: {e}")
            is_valid = self.twitch.validate_and_refresh_if_needed()
            if is_valid:
                if self.last_streamer_data:
                    self.data_loaded_signal.emit(self.last_streamer_data)
                self.show_main_signal.emit()
            else:
                QMetaObject.invokeMethod(self, "show_language_view", Qt.ConnectionType.QueuedConnection)
        
        if not self.twitch.access_token:
            QMetaObject.invokeMethod(self, "show_language_view", Qt.ConnectionType.QueuedConnection)
        else:
            threading.Thread(target=background_validate, daemon=True).start()

    def on_update_click(self):
        check_for_updates(parent_window=self, silent=False)

    def change_language(self, lang):
        self.lang = lang
        save_language(self.lang)
        self.t = load_translations(lang)
        self.update_ui_texts()
        self.refresh_favorites_list()

    @Slot()
    def _perform_auth_in_main_thread(self):
        success, message = self.twitch.start_login(self.on_login_success)
        self.label_status.setText(message)

    def update_ui_texts(self):
        self.title_label.setText(self.t.get("title", "⚡ RaidItBetter"))
        self.entry_streamer.setPlaceholderText(self.t.get("placeholder", "Streamer Name..."))
        self.btn_add_fav.setText(self.t.get("save_fav", "Hinzufügen"))
        self.btn_raid.setText(self.t.get("start_raid", "⚡ Raid starten"))
        self.checkbox_online.setText(self.t.get("only_online", "Nur Online Kanäle"))
        self.label_status.setText(self.t.get("ready", "Bereit"))

        current_data = self.combo_sort.currentData()
        
        self.combo_sort.blockSignals(True)
        self.combo_sort.clear()
        self.combo_sort.addItem(self.t.get("sort_custom", "Benutzerdefiniert"), "custom")
        self.combo_sort.addItem(self.t.get("sort_viewers_high", "Viewer: Hoch --> Niedrig"), "high_low")
        self.combo_sort.addItem(self.t.get("sort_viewers_low", "Viewer: Niedrig --> Hoch"), "low_high")
        
        index = self.combo_sort.findData(current_data)
        if index != -1:
            self.combo_sort.setCurrentIndex(index)
            
        self.combo_sort.blockSignals(False)
        
    def update_profile_button(self):
        def fetch():
            user_info = self.twitch.get_current_user_info()
            if user_info and "profile_image_url" in user_info:
                img_url = user_info["profile_image_url"]
                try:
                    import requests
                    data = requests.get(img_url).content
                    pixmap = QPixmap()
                    pixmap.loadFromData(QByteArray(data))
                    
                    size = 28
                    scaled = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatioByExpanding, Qt.TransformationMode.SmoothTransformation)
                    
                    rounded = QPixmap(size, size)
                    rounded.fill(Qt.GlobalColor.transparent)
                    
                    painter = QPainter(rounded)
                    painter.setRenderHint(QPainter.RenderHint.Antialiasing)
                    path = QPainterPath()
                    path.addEllipse(0, 0, size, size)
                    painter.setClipPath(path)
                    painter.drawPixmap(0, 0, scaled)
                    painter.end()
                
                    self.profile_updated_signal.emit(rounded)
                except Exception as e:
                    print(f"Error loading profile image: {e}")
                    self.profile_updated_signal.emit(None)
            else:
                self.profile_updated_signal.emit(None)
        
        if self.twitch.access_token:
            threading.Thread(target=fetch, daemon=True).start()
        else:
            self._apply_profile_image(None)

    @Slot(object)
    def _apply_profile_image(self, pixmap):
        if pixmap and not pixmap.isNull():
            icon = QIcon(pixmap)
            self.btn_profile.setIcon(icon)
            self.btn_profile.setText("")
            self.btn_profile.setIconSize(pixmap.size())
            self.btn_profile.setStyleSheet(HEADER_BTN_STYLE + " border: 1px solid #238636; padding: 0px; border-radius: 6px;")
            self.btn_profile.update()
        else:
            self.btn_profile.setIcon(QIcon())
            self.btn_profile.setText("👤")
            self.btn_profile.setStyleSheet(HEADER_BTN_STYLE)
            self.btn_profile.update()

    def toggle_online_filter(self, state):
        self.show_only_online = bool(state)
        if self.last_streamer_data:
            self._render_favorites_ui(self.last_streamer_data)

    @Slot(list)
    def _render_favorites_ui(self, streamer_data):
        scrollbar = self.list_favorites.verticalScrollBar()
        scroll_pos = scrollbar.value() if scrollbar else 0

        self.list_favorites.clear()

        display_data = [d for d in streamer_data if d["is_online"]] if self.show_only_online else streamer_data
        
        sort_data = self.combo_sort.currentData() if hasattr(self, "combo_sort") else "custom"
        
        is_custom_sort = (sort_data == "custom")

        if sort_data == "high_low":
            display_data.sort(key=lambda x: x.get("viewer_count", 0), reverse=True)
        elif sort_data == "low_high":
            display_data.sort(key=lambda x: x.get("viewer_count", 0), reverse=False)
        elif is_custom_sort:
            favorites = get_favorites_db()
            name_to_data = {d["name"].lower(): d for d in display_data}
            ordered_data = [name_to_data[n] for n in favorites if n in name_to_data]
            for d in display_data:
                if d["name"].lower() not in favorites:
                    ordered_data.append(d)
            display_data = ordered_data

        if not display_data:
            msg = self.t.get("no_online_favs", "Keine Online-Kanäle gefunden") if self.show_only_online else self.t.get("select_fav", "No favourites saved")
            item = QListWidgetItem(self.list_favorites)
            lbl = QLabel(f"❤️\n\n{msg}")
            lbl.setStyleSheet("color: #8b949e; background: transparent; padding: 20px; font-size: 13px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(lbl.sizeHint())
            self.list_favorites.setItemWidget(item, lbl)
        else:
            for i, data in enumerate(display_data):
                is_selected = (data["name"].lower() == str(self.select_streamer_name).lower())
                last_time = get_last_raid_for_channel(data['name'])
                
                list_item = QListWidgetItem(self.list_favorites)
                card = StreamerCard(
                    parent=self.list_favorites,
                    data=data,
                    is_selected=is_selected,
                    on_click=self.select_streamer,
                    on_delete=self.remove_favorite,
                    on_move_up=self.move_favorite_up,
                    on_move_down=self.move_favorite_down,
                    translations=self.t,
                    last_raid_time=last_time,
                    show_arrows=is_custom_sort 
                )
                list_item.setSizeHint(QSize(0, 100))
                self.list_favorites.addItem(list_item)
                self.list_favorites.setItemWidget(list_item, card)

        if scrollbar:
            scrollbar.setValue(scroll_pos)

    def start_auto_refresh(self):
        def background_refresh():
            favorites = get_favorites_db()
            if favorites:
                streamers_data = self.twitch.get_streamers_info(favorites)
                self.data_loaded_signal.emit(streamers_data)
        threading.Thread(target=background_refresh, daemon=True).start()

    def load_favorites_data(self, favorites, token):
        try:
            streamer_data = self.twitch.get_streamers_info(favorites)
            if token == self.load_token:
                self.last_streamer_data = streamer_data
                self.data_loaded_signal.emit(streamer_data)
        except Exception as e:
            print(f"[ERROR] Fehler in load_favorites_data: {e}")
        
    def refresh_favorites_list(self):
        self.load_token += 1
        current_token = self.load_token
        favorites = get_favorites_db()
        
        if not favorites:
            self.list_favorites.clear()
            item = QListWidgetItem(self.list_favorites)
            lbl = QLabel(f"❤️\n\n{self.t.get('select_fav', 'No favourites saved')}")
            lbl.setStyleSheet("color: #8b949e; background: transparent; padding: 20px; font-size: 13px;")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            item.setSizeHint(lbl.sizeHint())
            self.list_favorites.setItemWidget(item, lbl)
            return

        threading.Thread(target=self.load_favorites_data, args=(favorites, current_token), daemon=True).start()

    def select_streamer(self, name):
        self.select_streamer_name = name
        if self.last_streamer_data:
            self._render_favorites_ui(self.last_streamer_data)

    def add_favorite(self):
        streamer_name = self.entry_streamer.text().strip().lower()
        if not streamer_name:
            return
        if not re.match(r"^\w{1,25}$", streamer_name):
            self.label_status.setText(self.t.get("invalid_name", "Ungültiger Name"))
            return

        if add_favorite_db(streamer_name):
            self.refresh_favorites_list()
            self.label_status.setText(self.t.get("fav_added", "Hinzugefügt").format(name=streamer_name))
            self.entry_streamer.clear()
        else:
            self.label_status.setText(self.t.get("fav_exists", "Bereits vorhanden"))

    def remove_favorite(self, name):
        remove_favorite_db(name)
        if self.last_streamer_data:
            self.last_streamer_data = [d for d in self.last_streamer_data if d["name"].lower() != name.lower()]
        self.refresh_favorites_list()
        self.label_status.setText(f"Entfernt: {name}")

    def move_favorite_up(self, name):
        favorites = get_favorites_db()
        if name in favorites:
            idx = favorites.index(name)
            if idx > 0:
                favorites[idx], favorites[idx - 1] = favorites[idx - 1], favorites[idx]
                update_favorites_order(favorites)
                
                name_to_data = {d["name"].lower(): d for d in self.last_streamer_data}
                self.last_streamer_data = [name_to_data[n] for n in favorites if n in name_to_data]
                for d in self.last_streamer_data:
                    if d["name"].lower() not in favorites:
                        self.last_streamer_data.append(d)
                        
                self._render_favorites_ui(self.last_streamer_data)

    def move_favorite_down(self, name):
        favorites = get_favorites_db()
        if name in favorites:
            idx = favorites.index(name)
            if idx < len(favorites) - 1:
                favorites[idx], favorites[idx + 1] = favorites[idx + 1], favorites[idx]
                update_favorites_order(favorites)
                
                name_to_data = {d["name"].lower(): d for d in self.last_streamer_data}
                self.last_streamer_data = [name_to_data[n] for n in favorites if n in name_to_data]
                for d in self.last_streamer_data:
                    if d["name"].lower() not in favorites:
                        self.last_streamer_data.append(d)
                        
                self._render_favorites_ui(self.last_streamer_data)

    def handle_auth_click(self):
        if self.twitch.access_token:
            self.profile_menu.clear()

            user_info = self.twitch.get_current_user_info()
            username = user_info.get("display_name", "Eingeloggt") if user_info else "Eingeloggt"
            
            action_info = self.profile_menu.addAction(f"👤 {username}")
            action_info.setEnabled(False)
            
            self.profile_menu.addSeparator()
            
            action_logout = self.profile_menu.addAction("Abmelden")
            action_logout.triggered.connect(self.perform_logout)
            
            pos = self.btn_profile.mapToGlobal(QPoint(0, self.btn_profile.height() + 4))
            self.profile_menu.exec(pos)
        else:
            self.start_login_signal.emit()

    def on_login_success(self, event=None):
        self.show_main_signal.emit()
        msg = self.t.get("login_success", "Erfolgreich angemeldet")
        QTimer.singleShot(0, lambda: self.label_status.setText(msg))

    def perform_logout(self):
        self.twitch.logout()
        self.show_login_signal.emit()
        msg = self.t.get("logged_out", "Abgemeldet")
        QTimer.singleShot(0, lambda: self.label_status.setText(msg))

    def on_raid_click(self):
        streamer_name = self.entry_streamer.text().strip().lower()
        if not streamer_name and self.select_streamer_name:
            streamer_name = self.select_streamer_name.strip().lower()

        if not streamer_name and not self.is_raiding:
            self.label_status.setText(self.t.get("enter_name_raid", "Bitte Ziel eingeben"))
            return

        if not self.is_raiding:
            self.label_status.setText("Starte Raid...")

            def run():
                success, message = self.twitch.execute_raid(streamer_name)
                
                QTimer.singleShot(0, lambda: self.label_status.setText(message))
                
                if success:
                    self.is_raiding = True
                    self.raid_cancelled = False
                    
                    self.update_raid_btn_signal.emit("Raid abbrechen", BTN_RAID_CANCEL)
                    
                    add_raid_history_db(streamer_name, viewer_count=0, status="Success")
                    QTimer.singleShot(0, self.refresh_favorites_list)
                else:
                    QTimer.singleShot(0, self.reset_raid_button_state)
            threading.Thread(target=run, daemon=True).start()

        else:
            self.raid_cancelled = True
            QTimer.singleShot(0, lambda: self.label_status.setText("Breche Raid ab..."))

            def cancel_run():
                success, message = self.twitch.cancel_raid()
                QTimer.singleShot(0, lambda: self.label_status.setText(message))
                QTimer.singleShot(0, self.reset_raid_button_state)
            threading.Thread(target=cancel_run, daemon=True).start()
            
    def on_sort_changed(self):
        if self.last_streamer_data:
            self._render_favorites_ui(self.last_streamer_data)

    @Slot()
    def reset_raid_button_state(self):
        self.is_raiding = False
        self.btn_raid.setText(self.t.get("start_raid", "⚡ Raid starten"))
        self.btn_raid.setStyleSheet(BTN_RAID_START)
        
    @Slot(str, str)
    def _apply_raid_btn_style(self, text, style):
        self.btn_raid.setText(text)
        self.btn_raid.setStyleSheet(style)

    def on_language_selected(self, lang_code):
        self.change_language(lang_code)
        self.switch_view_animated(self.login_panel)

    @Slot()
    def show_language_view(self):
        self.switch_view_animated(self.language_panel)