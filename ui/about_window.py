from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from core.settings import APP_VERSION
from ui.styles.about_window_style import (
    ABOUT_WINDOW_STYLE, ABOUT_TEXT_STYLE, BTN_ACTION_STYLE
)

class Aboutwindow(QFrame):
    def __init__(self, parent, app_controller):
        super().__init__(parent)
        self.app = app_controller
        self.t = app_controller.t
        self.setFixedWidth(400)
        self.setStyleSheet(ABOUT_WINDOW_STYLE)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # Header als reiner Text (ohne störenden Rahmen oder Hintergrund)
        self.lbl_header = QLabel(self.t.get("about_title", "ℹ️ Über RaidItBetter"))
        self.lbl_header.setStyleSheet("""
            font-size: 16px !important;
            font-weight: bold !important;
            color: white !important;
            background: transparent !important;
            border: none !important;
            padding: 0px !important;
        """)
        layout.addWidget(self.lbl_header)

        # Info Text
        self.lbl_version = QLabel(f"{self.t.get('about_version', 'Version')}: {APP_VERSION}")
        self.lbl_version.setStyleSheet(ABOUT_TEXT_STYLE)
        layout.addWidget(self.lbl_version)

        # Description
        desc_text = self.t.get("about_description", "Ein simples Tool zum Verwalten von Raids")
        full_desc = f"{desc_text}\n\nDev: Paddi0010"
        self.lbl_desc = QLabel(full_desc)
        self.lbl_desc.setWordWrap(True)
        self.lbl_desc.setStyleSheet("font-size: 12px !important; color: #8b949e !important; background: transparent !important; border: none !important;")
        layout.addWidget(self.lbl_desc)

        layout.addStretch()

        # Close Button
        self.btn_close = QPushButton(self.t.get("close", "Schließen"))
        self.btn_close.setFixedHeight(35)
        self.btn_close.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_close.setStyleSheet(BTN_ACTION_STYLE)
        self.btn_close.clicked.connect(self.app.toggle_about)
        layout.addWidget(self.btn_close)

    def update_texts(self):
        self.t = self.app.t
        self.lbl_header.setText(self.t.get("about_title", "ℹ️ Über RaidItBetter"))
        self.lbl_version.setText(f"{self.t.get('about_version', 'Version')}: {APP_VERSION}")
        
        desc_text = self.t.get("about_description", "Ein simples Tool zum Verwalten von Raids")
        self.lbl_desc.setText(f"{desc_text}\n\nDev: Paddi0010")
        
        self.btn_close.setText(self.t.get("close", "Schließen"))