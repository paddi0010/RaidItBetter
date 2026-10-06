from PySide6.QtCore import QSettings, Qt
from PySide6.QtWidgets import (
    QFrame, QLineEdit, QVBoxLayout, QHBoxLayout, 
    QLabel, QComboBox, QPushButton, QMessageBox, QTabWidget, QWidget
)
# Clipboard wird für den Kopieren-Button benötigt:
from PySide6.QtGui import QClipboard
from PySide6.QtWidgets import QApplication

import logging
import os
from core.config import CLIENT_ID, REDIRECT_URI, CLIENT_SECRET
from ui.styles.settings_style import BTN_SETTINGS_ACTION, COMBOBOX_STYLE, SETTINGS_LABEL_STYLE, SETTINGS_WINDOW_STYLE

logger = logging.getLogger("RaidItBetter")

class SettingsPanel(QFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.t = app_controller.t
        self.setFixedWidth(420)
        self.setStyleSheet(SETTINGS_WINDOW_STYLE)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(10)

        # Header Titel
        self.lbl_header = QLabel(self.t.get("settings_title", "⚙️ Einstellungen"))
        self.lbl_header.setStyleSheet(SETTINGS_LABEL_STYLE)
        main_layout.addWidget(self.lbl_header)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #333333; border-radius: 4px; background: transparent; }
            QTabBar::tab { background: #1e1e1e; color: #a0a0a0; padding: 8px 15px; border-top-left-radius: 4px; border-top-right-radius: 4px; margin-right: 2px; }
            QTabBar::tab:selected { background: #2b2b2b; color: #ffffff; font-weight: bold; }
        """)

        # 1. Tab
        self.tab_general = QWidget()
        general_layout = QVBoxLayout(self.tab_general)
        
        self.lbl_lang = QLabel(self.t.get("settings_language", "Sprache / Language:"))
        self.lbl_lang.setStyleSheet(SETTINGS_LABEL_STYLE)
        general_layout.addWidget(self.lbl_lang)

        current_choice = "Deutsch" if getattr(self.app, "lang", "de") == "de" else "English"
        self.lang_menu = QComboBox()
        font = self.lang_menu.font()
        font.setPointSize(10)
        self.lang_menu.setFont(font)
        self.lang_menu.addItems(["Deutsch", "English"])
        self.lang_menu.setCurrentText(current_choice)
        self.lang_menu.setFixedHeight(35)
        self.lang_menu.setStyleSheet(COMBOBOX_STYLE)
        self.lang_menu.currentTextChanged.connect(self.on_language_change)
        general_layout.addWidget(self.lang_menu)
        general_layout.addStretch()
        
        self.tabs.addTab(self.tab_general, "Allgemein")

        # 2. Tab: Twitch API & Credentials
        self.tab_twitch = QWidget()
        twitch_layout = QVBoxLayout(self.tab_twitch)
        twitch_layout.setSpacing(10)

        self.settings = QSettings("TwitchRaidApp", "RaidItBetter")
        
        default_client_id = self.settings.value("twitch/client_id", "")
        if not default_client_id:
            default_client_id = CLIENT_ID or os.getenv("CLIENT_ID", "")
            
        default_secret = self.settings.value("twitch/client_secret", "")
        if not default_secret:
            default_secret = CLIENT_SECRET or os.getenv("CLIENT_SECRET", "")
            
        default_oauth = self.settings.value("twitch/oauth_token", "")
        if not default_oauth:
            default_oauth = os.getenv("OAUTH_TOKEN", "") or os.getenv("TWITCH_OAUTH_TOKEN", "")

        def create_field_with_copy(label_text, is_password=False, is_readonly=False):
            lbl = QLabel(label_text)
            lbl.setStyleSheet(SETTINGS_LABEL_STYLE)
            twitch_layout.addWidget(lbl)

            row_layout = QHBoxLayout()
            row_layout.setSpacing(5)

            field = QLineEdit()
            field.setFixedHeight(35)
            if is_password:
                field.setEchoMode(QLineEdit.EchoMode.Password)
            if is_readonly:
                field.setReadOnly(True)
                field.setStyleSheet("""
                    QLineEdit {
                        background-color: #1e1e1e; 
                        color: #cccccc; 
                        border: 1px solid #333333; 
                        border-radius: 4px; 
                        padding-left: 8px;
                    }
                """)
            
            btn_copy = QPushButton("📋")
            btn_copy.setFixedSize(35, 35)
            btn_copy.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_copy.setToolTip("In Zwischenablage kopieren")
            
            btn_copy.clicked.connect(lambda: self.copy_to_clipboard(field.text(), btn_copy))

            row_layout.addWidget(field)
            row_layout.addWidget(btn_copy)
            twitch_layout.addLayout(row_layout)
            return field

        self.client_id_input = create_field_with_copy("Client ID")
        self.client_id_input.setPlaceholderText("Client ID eingeben...")
        self.client_id_input.setText(default_client_id)
        self.client_id_input.returnPressed.connect(self.save_twitch_settings)

        self.client_secret_input = create_field_with_copy("Client Secret", is_password=True)
        self.client_secret_input.setPlaceholderText("Client Secret eingeben...")
        self.client_secret_input.setText(default_secret)
        self.client_id_input.returnPressed.connect(self.save_twitch_settings)

        lbl_oauth = QLabel("OAuth Token")
        lbl_oauth.setStyleSheet(SETTINGS_LABEL_STYLE)
        twitch_layout.addWidget(lbl_oauth)

        oauth_row = QHBoxLayout()
        oauth_row.setSpacing(5)

        self.oauth_input = QLineEdit()
        self.oauth_input.setFixedHeight(35)
        self.oauth_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.oauth_input.setPlaceholderText("Wird beim Login automatisch generiert...")
        self.oauth_input.setText(default_oauth)
        self.oauth_input.setReadOnly(True)
        self.oauth_input.setStyleSheet("""
            QLineEdit {
                background-color: #1e1e1e; 
                color: #cccccc; 
                border: 1px solid #333333; 
                border-radius: 4px; 
                padding-left: 8px;
            }
        """)

        self.btn_toggle_token = QPushButton("👁️")
        self.btn_toggle_token.setFixedSize(35, 35)
        self.btn_toggle_token.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_toggle_token.setToolTip("Token anzeigen")
        self.btn_toggle_token.clicked.connect(self.toggle_token_visibility)

        self.btn_copy_oauth = QPushButton("📋")
        self.btn_copy_oauth.setFixedSize(35, 35)
        self.btn_copy_oauth.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_copy_oauth.setToolTip("Token kopieren")
        self.btn_copy_oauth.clicked.connect(lambda: self.copy_to_clipboard(self.oauth_input.text(), self.btn_copy_oauth))

        oauth_row.addWidget(self.oauth_input)
        oauth_row.addWidget(self.btn_toggle_token)
        oauth_row.addWidget(self.btn_copy_oauth)
        twitch_layout.addLayout(oauth_row)

        twitch_layout.addStretch()

        # Save button for api
        self.btn_save_api = QPushButton("API-Daten speichern")
        self.btn_save_api.setFixedHeight(35)
        self.btn_save_api.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_save_api.setStyleSheet(BTN_SETTINGS_ACTION)
        self.btn_save_api.clicked.connect(self.save_twitch_settings)
        twitch_layout.addWidget(self.btn_save_api)

        self.tabs.addTab(self.tab_twitch, "Twitch API")
        
        main_layout.addWidget(self.tabs)

        # Close-Button
        self.btn_close = QPushButton(self.t.get("close", "Schließen"))
        self.btn_close.setFixedHeight(35)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(BTN_SETTINGS_ACTION)
        self.btn_close.clicked.connect(self.app.toggle_settings)
        main_layout.addWidget(self.btn_close)

    def copy_to_clipboard(self, text, button_widget):
        if not text:
            return
        clipboard = QApplication.clipboard()
        clipboard.setText(text)
        
        original_text = button_widget.text()
        button_widget.setText("✔️")
        from PySide6.QtCore import QTimer
        QTimer.singleShot(1500, lambda: button_widget.setText(original_text))
        logger.info("Wert wurde in die Zwischenablage kopiert.")

    def on_language_change(self, choice):
        lang_code = "de" if choice == "Deutsch" else "en"
        if hasattr(self.app, "change_language"):
            self.app.change_language(lang_code)
            self.update_texts()

    def update_texts(self):
        self.t = self.app.t
        self.lbl_header.setText(self.t.get("settings_title", "⚙️ Einstellungen"))
        self.lbl_lang.setText(self.t.get("settings_language", "Sprache / Language:"))
        self.btn_close.setText(self.t.get("close", "Schließen"))
        
    def save_twitch_settings(self):
        client_id = self.client_id_input.text().strip()
        client_secret = self.client_secret_input.text().strip()
        oauth_token = self.oauth_input.text().strip()
    
        self.settings.setValue("twitch/client_id", client_id)
        self.settings.setValue("twitch/client_secret", client_secret)
        self.settings.setValue("twitch/oauth_token", oauth_token)
        
        logger.info("Twitch API-Daten wurden über die Einstellungen aktualisiert.")
        self.btn_save_api.setText("✅ Gespeichert")
        
    def update_oauth_token(self, new_token: str):
        self.oauth_input.setText(new_token)
        self.settings.setValue("twitch/oauth_token", new_token)
        logger.info("OAuth-Token wurde durch den Login-Flow automatisch aktualisiert.")

    def toggle_token_visibility(self):
        is_masked = self.oauth_input.echoMode() == QLineEdit.EchoMode.Password
        
        if is_masked:
            reply = QMessageBox.warning(
                self,
                "Sicherheitshinweis",
                "⚠️ Achtung!\n\nDein OAuth-Token gewährt Zugriff auf deinen Twitch-Account.\n"
                "Möchtest du das Token wirklich unmaskiert anzeigen?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.oauth_input.setEchoMode(QLineEdit.EchoMode.Normal)
                self.btn_toggle_token.setText("🔒")
                self.btn_toggle_token.setToolTip("Token verbergen")
        else:
            self.oauth_input.setEchoMode(QLineEdit.EchoMode.Password)
            self.btn_toggle_token.setText("👁️")
            self.btn_toggle_token.setToolTip("Token anzeigen")