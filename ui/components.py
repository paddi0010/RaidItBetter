import customtkinter as ctk
from ui.styles import BG_CARD, COLOR_DANGER

class StreamerCard(ctk.CTkFrame):
    def __init__(self, parent, data, is_selected, on_click, on_delete, translations, last_raid_time):
        border_width = 2 if is_selected else 0
        border_color = "#1f6aa5" if is_selected else None
        
        super().__init__(
            parent, 
            fg_color=BG_CARD, 
            corner_radius=6,
            border_width=border_width,
            border_color=border_color
        )
        
        self.pack(pady=4, fill="x", padx=5)
        self.bind("<Button-1>", lambda e: on_click(data["name"]))

        dot_color = "green" if data["is_online"] else "gray"
        lbl_dot = ctk.CTkLabel(self, text="●", text_color=dot_color, font=ctk.CTkFont(size=14))
        lbl_dot.pack(side="left", padx=(10, 6))
        lbl_dot.bind("<Button-1>", lambda e: on_click(data["name"]))

        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(side="left", fill="both", expand=True, pady=8, padx=5)
        info_frame.bind("<Button-1>", lambda e: on_click(data["name"]))

        status_text = translations.get("online", "Online") if data["is_online"] else translations.get("offline", "Offline")
        name_text = f"{data['name']} ({status_text})"
        
        lbl_name = ctk.CTkLabel(info_frame, text=name_text, font=ctk.CTkFont(size=12, weight="bold"), anchor="w")
        lbl_name.pack(fill="x")
        lbl_name.bind("<Button-1>", lambda e: on_click(data["name"]))

        if data["is_online"]:
            details = data.get('game_name', '')
        else:
            if not last_raid_time:
                last_raid_time = translations.get("never", "Nie")
            details = translations.get("last_raided", "Last Raid: {date}").format(date=last_raid_time)
            
        lbl_details = ctk.CTkLabel(info_frame, text=details, font=ctk.CTkFont(size=10), text_color="gray", anchor="w")
        lbl_details.pack(fill="x")
        lbl_details.bind("<Button-1>", lambda e: on_click(data["name"]))

        btn_del = ctk.CTkButton(
            self, text="✕", width=25, height=25, 
            fg_color="transparent", hover_color=COLOR_DANGER, 
            text_color="gray", command=lambda: on_delete(data["name"])
        )
        btn_del.pack(side="right", padx=8)