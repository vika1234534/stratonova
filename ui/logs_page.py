import customtkinter as ctk
from ui.theme import *
from ui.widgets import tree_with_scroll, page_header, separator, btn


class LogsPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=C_BG_MAIN, corner_radius=0)
        self.user = user
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "📋  Журнал событий")
        separator(self)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(8, 10))
        btn(toolbar, "🔄  Обновить", self.refresh, style="secondary", width=130).pack(side="left")

        cols = [
            ("ID",       50, "center"),
            ("Дата",    145, "center"),
            ("Пользователь", 160, "w"),
            ("Роль",    100, "center"),
            ("Действие",160, "w"),
            ("Детали",  340, "w"),
        ]
        frame, self._tree = tree_with_scroll(self, cols, height=26)
        frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))

        self._status = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=C_TEXT_MUTED)
        self._status.pack(anchor="w", padx=24, pady=(0, 8))

    def refresh(self):
        from services.log_service import get_logs
        rows = get_logs()
        for item in self._tree.get_children():
            self._tree.delete(item)
        for i, r in enumerate(rows):
            dt = r["created_at"].strftime("%d.%m.%Y %H:%M:%S") if hasattr(r["created_at"], "strftime") else str(r["created_at"])
            role = "Администратор" if r.get("role") == "admin" else "Кладовщик"
            tag = "odd" if i % 2 else "even"
            self._tree.insert("", "end", tags=(tag,), values=(
                r["id"], dt,
                r.get("full_name") or "—",
                role,
                r.get("action") or "—",
                r.get("details") or "—",
            ))
        self._status.configure(text=f"Записей: {len(rows)}")
