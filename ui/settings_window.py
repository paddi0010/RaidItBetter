from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QComboBox, QPushButton
from ui.styles.settings_style import (
    SETTINGS_WINDOW_STYLE, SETTINGS_CONTAINER_STYLE, SETTINGS_LABEL_STYLE,
    SETTINGS_TITLE_STYLE, COMBOBOX_STYLE, BTN_SETTINGS_ACTION
)

class SettingsPanel(QFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.t = app_controller.t 
        self.setFixedWidth(400)
        self.setStyleSheet(SETTINGS_WINDOW_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header
        self.lbl_header = QLabel(self.t.get("settings_title", "⚙️ Einstellungen"))
        self.lbl_header.setStyleSheet(SETTINGS_LABEL_STYLE)
        layout.addWidget(self.lbl_header)

        # Language-Settings
        self.lbl_lang = QLabel(self.t.get("settings_language", "Sprache / Language:"))
        self.lbl_lang.setStyleSheet(SETTINGS_LABEL_STYLE)
        layout.addWidget(self.lbl_lang)

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
        layout.addWidget(self.lang_menu)

        layout.addStretch()

        # Close-Button
        self.btn_close = QPushButton(self.t.get("close", "Schließen"))
        self.btn_close.setFixedHeight(35)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(BTN_SETTINGS_ACTION)
        self.btn_close.clicked.connect(self.app.toggle_settings)
        layout.addWidget(self.btn_close)

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