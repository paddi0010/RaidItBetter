from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QPushButton, 
    QLabel, QScrollArea, QWidget, QFrame
)
from services.database import get_raid_history_db, clear_raid_history_db
from ui.styles.history_style import (
    HISTORY_WINDOW_STYLE, HISTORY_SCROLL_AREA_STYLE, HISTORY_ITEM_STYLE,
    HISTORY_TITLE_STYLE, BTN_HISTORY_ACTION
)

class RaidHistoryWindow(QFrame):
    def __init__(self, parent, translations):
        super().__init__(parent)
        self.t = translations
        self.setStyleSheet(HISTORY_WINDOW_STYLE)

        # main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Top Frame (Titel + Clear Button)
        top_frame = QWidget()
        top_layout = QHBoxLayout(top_frame)
        top_layout.setContentsMargins(0, 0, 0, 0)

        lbl_title = QLabel(self.t.get("history_title", "📜 Letzte Raids"))
        lbl_title.setStyleSheet(HISTORY_TITLE_STYLE)
        top_layout.addWidget(lbl_title)

        btn_clear = QPushButton(self.t.get("history_clear", "🗑️ Clear"))
        btn_clear.setFixedSize(75, 28)
        btn_clear.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_clear.setStyleSheet(BTN_HISTORY_ACTION)
        btn_clear.clicked.connect(self.clear_history)
        top_layout.addWidget(btn_clear)

        main_layout.addWidget(top_frame)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet(HISTORY_SCROLL_AREA_STYLE)

        self.scroll_content = QWidget()
        self.scroll_layout = QVBoxLayout(self.scroll_content)
        self.scroll_layout.setContentsMargins(10, 10, 10, 10)
        self.scroll_layout.setSpacing(8)
        self.scroll_area.setWidget(self.scroll_content)

        main_layout.addWidget(self.scroll_area)

        self.load_history_data()

    def load_history_data(self):
        for i in reversed(range(self.scroll_layout.count())): 
            widget = self.scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        history_data = get_raid_history_db()
        if not history_data:
            lbl_empty = QLabel(self.t.get("history_empty", "Noch keine Raids aufgezeichnet."))
            lbl_empty.setStyleSheet(HISTORY_ITEM_STYLE)
            lbl_empty.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.scroll_layout.addWidget(lbl_empty)
            return

        for row in history_data:
            timestamp, target, viewers, status = row
            
            card = QFrame()
            card.setStyleSheet(HISTORY_WINDOW_STYLE)
            card_layout = QVBoxLayout(card)
            card_layout.setContentsMargins(10, 10, 10, 10)

            t_label = self.t.get("history_target", "🎯 Ziel")
            time_label = self.t.get("history_time", "🕒 Zeit")
            status_label = self.t.get("history_status", "📊 Status")

            text_content = f"{t_label}: {target}\n{time_label}: {timestamp}\n{status_label}: {status}"
            lbl_item = QLabel(text_content)
            lbl_item.setStyleSheet(HISTORY_ITEM_STYLE)
            card_layout.addWidget(lbl_item)

            self.scroll_layout.addWidget(card)
        
        self.scroll_layout.addStretch()

    def clear_history(self):
        clear_raid_history_db()
        self.load_history_data()