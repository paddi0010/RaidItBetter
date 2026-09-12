import customtkinter as ctk

COLOR_PRIMARY = "#9146FF"      # Twitch Purple
COLOR_PRIMARY_HOVER = "#772ce8"
COLOR_SUCCESS = "#28a745"      # Grün
COLOR_DANGER = "#d9534f"       # Rot / Löschen
COLOR_DANGER_HOVER = "#c9302c"
COLOR_RAID = "#e91916"         # Raid Button
COLOR_RAID_HOVER = "#c81310"

BG_CARD = ("white", "gray22")
BG_SCROLL = ("gray92", "gray17")
TEXT_MUTED = "gray"

# Buttons
BTN_GREEN = "#28a745"
BTN_ORANGE = "#ff851b"
BTN_GRAY = ("gray85", "gray25")
BTN_GRAY_HOVER = ("gray75", "gray35")

# --- Fonts ---
def get_font_title(size=20):
    return ctk.CTkFont(size=size, weight="bold")

def get_font_bold(size=12):
    return ctk.CTkFont(size=size, weight="bold")

def get_font_normal(size=12):
    return ctk.CTkFont(size=size)