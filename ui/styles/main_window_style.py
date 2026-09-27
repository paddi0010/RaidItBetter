MAIN_WINDOW_STYLE = "background-color: #0d1117; color: white;"

STREAMER_CARD_STYLE = """
    QFrame {{
        background-color: {bg_color};
        border: 1px solid {border_color};
        border-radius: 8px;
    }}
    QFrame:hover {{
        background-color: #30363d;
        border: 1px solid #30363d;
    }}
"""

STREAMER_CARD_DELETE_BTN = """
    QPushButton {
        background-color: transparent;
        color: #484f58;
        border: none;
        border-radius: 4px;
        font-weight: bold;
        font-size: 12px;
    }
    QPushButton:hover {
        background-color: rgba(217, 83, 79, 0.15);
        color: #f85149;
    }
"""

PROFILE_MENU = """
    QMenu {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
        color: #c9d1d9;
        padding: 6px;
    }
    QMenu::item {
        padding: 8px 24px;
        border-radius: 4px;
    }
    QMenu::item:selected {
        background-color: #21262d;
        color: white;
    }
    QMenu::separator {
        height: 1px;
        background: #30363d;
        margin: 4px 0px;
    }
"""

HEADER_BTN_STYLE = """
    QPushButton { 
        background-color: #21262d; 
        color: white; 
        border: 1px solid #30363d; 
        border-radius: 6px; 
        font-size: 14px; 
    }
    QPushButton:hover { 
        background-color: #30363d; 
    }
"""

INPUT_CONTAINER_STYLE = "background-color: #161b22; border-radius: 8px; border: 1px solid #30363d;"

ENTRY_STREAMER_STYLE = """
    background-color: #0d1117; 
    color: white; 
    border: 1px solid #30363d; 
    border-radius: 6px; 
    padding-left: 8px;
"""

BTN_ADD_FAV_STYLE = """
    QPushButton { 
        background-color: #21262d; 
        color: white; 
        border: 1px solid #30363d; 
        border-radius: 6px; 
        font-weight: bold; 
        padding: 0 12px; 
    }
    QPushButton:hover { 
        background-color: #30363d; 
    }
"""

SCROLL_AREA_STYLE = """
    QListWidget {
        background-color: #0d1117;
        border: 1px solid #21262d;
        border-radius: 6px;
        outline: none; /* Entfernt den Fokus-Rahmen des Widgets */
    }
    QListWidget::item {
        background: transparent;
        border: none;
        outline: none; /* Entfernt den Rahmen um einzelne Items */
    }
    QListWidget::item:selected {
        background: transparent;
        border: none;
        outline: none;
    }
    QListWidget::item:focus {
        border: none;
        outline: none;
    }
"""

BTN_RAID_START = """
    QPushButton { 
        background-color: #e91916; 
        color: white; 
        border-radius: 6px; 
        font-size: 14px; 
        font-weight: bold; 
    }
    QPushButton:hover { 
        background-color: #c81310; 
    }
"""

BTN_RAID_CANCEL = """
    QPushButton { 
        background-color: #21262d; 
        color: white; 
        border-radius: 6px; 
        font-size: 14px; 
        font-weight: bold; 
    }
    QPushButton:hover { 
        background-color: #30363d; 
    }
"""

STATUSBAR_STYLE = "color: #8b949e; font-size: 11px; padding: 4px; background-color: #161b22; border-top: 1px solid #30363d;"

PROGRESS_BAR = """
    QProgressBar {
        background-color: #21262d;
        border: none;
        border-radius: 3px;
    }
    QProgressBar::chunk {
        background-color: #9146FF;
        border-radius: 3px;
    }
"""