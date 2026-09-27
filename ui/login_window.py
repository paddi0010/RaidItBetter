from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFrame, QVBoxLayout, QLabel, QPushButton
from ui.styles.login_window_style import BTN_LOGIN

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
        
        desc = QLabel(
            "Um Raids auszuführen und deine Favoriten optimal zu verwalten, "
            "ist eine Anmeldung mit deinem Twitch-Account erforderlich."
        )
        desc.setWordWrap(True)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setStyleSheet("font-size: 14px; color: #8b949e; background: transparent;")
        layout.addWidget(desc)
        
        layout.addSpacing(20)
        
        btn_login = QPushButton("Mit Twitch anmelden 🚀")
        btn_login.setFixedHeight(50)
        btn_login.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_login.setStyleSheet(BTN_LOGIN)
        btn_login.clicked.connect(self.main_app.handle_auth_click)
        layout.addWidget(btn_login)
        
        layout.addStretch()