import customtkinter as ctk
from database import get_raid_history_db, clear_raid_history_db
from ui.styles import BG_CARD, BG_SCROLL, COLOR_DANGER, COLOR_DANGER_HOVER, get_font_title, get_font_bold

class RaidHistoryWindow(ctk.CTkToplevel):
    def __init__(self, parent, translations):
        super().__init__(parent)
        self.t = translations
        self.title("RaidItBetter - Raid History")
        
        width = 400
        height = 450
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        self.update_idletasks()
        parent_x = parent.winfo_x()
        parent_y = parent.winfo_y()
        parent_w = parent.winfo_width()
        parent_h = parent.winfo_height()

        x = parent_x + (parent_w // 2) - (width // 2)
        y = parent_y + (parent_h // 2) - (height // 2)
        self.geometry(f"{width}x{height}+{x}+{y}")

        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(pady=(15, 10), fill="x", padx=20)

        lbl_title = ctk.CTkLabel(top_frame, text=self.t.get("history_title", "📜 Letzte Raids"), font=ctk.CTkFont(size=16, weight="bold"))
        lbl_title.pack(side="left")

        btn_clear = ctk.CTkButton(
            top_frame, text=self.t.get("history_clear", "🗑️ Clear"), width=75, height=28,
            fg_color="#d9534f", hover_color="#c9302c",
            font=ctk.CTkFont(size=11, weight="bold"),
            command=self.clear_history
        )
        btn_clear.pack(side="right")

        self.scroll_frame = ctk.CTkScrollableFrame(self, width=360, height=360, fg_color=("gray92", "gray17"))
        self.scroll_frame.pack(pady=5, padx=20)

        self.load_history_data()

    def load_history_data(self):
        for w in self.scroll_frame.winfo_children():
            w.destroy()

        history_data = get_raid_history_db()
        if not history_data:
            lbl_empty = ctk.CTkLabel(self.scroll_frame, text=self.t.get("history_empty", "Noch keine Raids aufgezeichnet."), text_color="gray")
            lbl_empty.pack(pady=20)
            return

        for row in history_data:
            timestamp, target, viewers, status = row
            card = ctk.CTkFrame(self.scroll_frame, fg_color=("white", "gray22"), corner_radius=6)
            card.pack(pady=4, fill="x", padx=5)

            t_label = self.t.get("history_target", "🎯 Ziel")
            time_label = self.t.get("history_time", "🕒 Zeit")
            status_label = self.t.get("history_status", "📊 Status")

            text_content = f"{t_label}: {target}\n{time_label}: {timestamp}\n{status_label}: {status}"
            lbl_item = ctk.CTkLabel(card, text=text_content, font=ctk.CTkFont(size=11), justify="left", anchor="w")
            lbl_item.pack(pady=8, padx=10, fill="x")

    def clear_history(self):
        clear_raid_history_db()
        self.load_history_data()