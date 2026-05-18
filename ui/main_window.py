import customtkinter as ctk
from ui.theme import *


class MainWindow(ctk.CTkFrame):
    NAV = [
        ("🏠", "Главная",          "dashboard"),
        ("📦", "Материалы",        "materials"),
        ("📥", "Поступление",      "receipts"),
        ("📤", "Списание",         "writeoff"),
        ("📊", "Отчёты",           "reports"),
        ("📋", "Журнал событий",   "logs"),
    ]

    def __init__(self, master, user: dict, on_logout):
        super().__init__(master)
        self.user = user
        self.on_logout = on_logout
        self.pack(fill="both", expand=True)
        self._pages: dict = {}
        self._nav_btns: dict = {}
        self._build()
        self._show("dashboard")

    def _build(self):
        # ── Боковое меню ────────────────────────────────────
        self.sidebar = ctk.CTkFrame(self, fg_color=C_BG_SIDEBAR,
                                    width=SIDEBAR_W, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        # Лого
        logo_frame = ctk.CTkFrame(self.sidebar, fg_color="#0F1F15", corner_radius=0)
        logo_frame.pack(fill="x")
        ctk.CTkLabel(logo_frame, text="🌿 ТК Новочебоксарский",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=C_GREEN_ULTRA).pack(pady=16, padx=16)

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#1F3D28",
                     corner_radius=0).pack(fill="x")

        # Аватар пользователя
        user_frame = ctk.CTkFrame(self.sidebar, fg_color="#112219", corner_radius=0)
        user_frame.pack(fill="x", pady=(0, 8))

        av = ctk.CTkFrame(user_frame, width=38, height=38,
                          fg_color=C_GREEN_ACCENT, corner_radius=19)
        av.pack(side="left", padx=14, pady=12)
        av.pack_propagate(False)
        initials = "".join(w[0].upper() for w in self.user["full_name"].split()[:2])
        ctk.CTkLabel(av, text=initials[:2],
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color="white").place(relx=0.5, rely=0.5, anchor="center")

        info = ctk.CTkFrame(user_frame, fg_color="transparent")
        info.pack(side="left", pady=12)
        role_txt = "Администратор" if self.user["role"] == "admin" else "Кладовщик"
        name = self.user["full_name"]
        short = name if len(name) <= 18 else name[:16] + "…"
        ctk.CTkLabel(info, text=short,
                     font=(FONT_FAMILY, 11, "bold"),
                     text_color="white").pack(anchor="w")

        badge = ctk.CTkFrame(info, fg_color=C_GREEN_PRIMARY, corner_radius=4)
        badge.pack(anchor="w", pady=(2, 0))
        ctk.CTkLabel(badge, text=role_txt,
                     font=(FONT_FAMILY, 9),
                     text_color=C_GREEN_ULTRA).pack(padx=6, pady=1)

        ctk.CTkFrame(self.sidebar, height=1, fg_color="#1F3D28",
                     corner_radius=0).pack(fill="x")

        # Навигация
        nav_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        nav_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(nav_frame, text="НАВИГАЦИЯ",
                     font=(FONT_FAMILY, 9),
                     text_color="#4A6B52").pack(anchor="w", padx=6, pady=(4, 8))

        for icon, label, key in self.NAV:
            btn = ctk.CTkButton(nav_frame,
                                text=f"  {icon}   {label}",
                                **BTN_NAV,
                                command=lambda k=key: self._show(k))
            btn.pack(fill="x", pady=2)
            self._nav_btns[key] = btn

        # Кнопка выхода
        ctk.CTkFrame(self.sidebar, height=1, fg_color="#1F3D28",
                     corner_radius=0).pack(fill="x", side="bottom", pady=(0, 0))
        ctk.CTkButton(self.sidebar,
                      text="  🚪   Выйти",
                      fg_color="transparent",
                      hover_color="#3D1515",
                      text_color="#E88",
                      anchor="w",
                      height=44,
                      font=(FONT_FAMILY, 13),
                      corner_radius=0,
                      command=self._logout).pack(fill="x", side="bottom")

        # ── Контент ─────────────────────────────────────────
        self.content = ctk.CTkFrame(self, fg_color=C_BG_MAIN, corner_radius=0)
        self.content.pack(side="left", fill="both", expand=True)

    def _show(self, key: str):
        for k, b in self._nav_btns.items():
            if k == key:
                b.configure(**BTN_NAV_ACTIVE)
            else:
                b.configure(**BTN_NAV)

        for page in self._pages.values():
            page.pack_forget()

        if key not in self._pages:
            self._pages[key] = self._create(key)

        self._pages[key].pack(fill="both", expand=True)

        if key == "dashboard" and hasattr(self._pages[key], "refresh"):
            self._pages[key].refresh()

    def _create(self, key):
        from ui.dashboard_page import DashboardPage
        from ui.materials_page import MaterialsPage
        from ui.receipts_page  import ReceiptsPage
        from ui.writeoff_page  import WriteoffPage
        from ui.reports_page   import ReportsPage
        from ui.logs_page      import LogsPage

        pages = {
            "dashboard": lambda: DashboardPage(self.content, self.user),
            "materials": lambda: MaterialsPage(self.content, self.user),
            "receipts":  lambda: ReceiptsPage(self.content, self.user),
            "writeoff":  lambda: WriteoffPage(self.content, self.user),
            "reports":   lambda: ReportsPage(self.content, self.user),
            "logs":      lambda: LogsPage(self.content, self.user),
        }
        return pages[key]()

    def _logout(self):
        from ui.widgets import ConfirmDialog
        d = ConfirmDialog(self, "Выход", "Вы действительно хотите выйти из системы?")
        if d.result:
            self.destroy()
            self.on_logout()
