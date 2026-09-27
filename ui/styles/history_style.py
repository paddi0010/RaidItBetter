HISTORY_WINDOW_STYLE = """
    QWidget {
        background-color: #0d1117;
        color: white;
    }
"""

HISTORY_SCROLL_AREA_STYLE = """
    QScrollArea { 
        background-color: #161b22; 
        border: 1px solid #30363d; 
        border-radius: 8px; 
    }
    QWidget { 
        background-color: #161b22; 
    }
    QScrollBar:vertical {
        background: #161b22;
        width: 6px;
        margin: 0px;
        border-radius: 3px;
    }
    QScrollBar::handle:vertical {
        background: #30363d;
        border-radius: 3px;
        min-height: 20px;
    }
    QScrollBar::handle:vertical:hover {
        background: #8b949e;
    }
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
        height: 0px;
    }
"""

HISTORY_ITEM_STYLE = """
    QFrame {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 6px;
    }
"""

HISTORY_TITLE_STYLE = """
    color: white;
    font-size: 16px;
    font-weight: bold;
    background: transparent;
    border: none;
"""

BTN_HISTORY_ACTION = """
    QPushButton {
        background-color: #21262d;
        color: white;
        border: 1px solid #30363d;
        border-radius: 6px;
        font-weight: bold;
        padding: 6px 12px;
    }
    QPushButton:hover {
        background-color: #30363d;
    }
"""