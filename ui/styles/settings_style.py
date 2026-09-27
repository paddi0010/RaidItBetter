SETTINGS_WINDOW_STYLE = """
    QWidget {
        background-color: #0d1117;
        color: white;
    }
"""

SETTINGS_CONTAINER_STYLE = """
    QFrame {
        background-color: #161b22;
        border: 1px solid #30363d;
        border-radius: 8px;
    }
"""

SETTINGS_LABEL_STYLE = """
    color: #c9d1d9;
    font-size: 13px;
    background: transparent;
    border: none;
"""

SETTINGS_TITLE_STYLE = """
    color: white;
    font-size: 16px;
    font-weight: bold;
    background: transparent;
    border: none;
"""

COMBOBOX_STYLE = """
    QComboBox {
        background-color: #0d1117;
        color: white;
        border: 1px solid #30363d;
        border-radius: 6px;
        padding: 5px 10px;
    }
    QComboBox::drop-down {
        border: none;
    }
    QComboBox QAbstractItemView {
        background-color: #161b22;
        color: white;
        selection-background-color: #30363d;
    }
"""

BTN_SETTINGS_ACTION = """
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