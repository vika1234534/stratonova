import customtkinter as ctk
from ui.theme import *
from ui.widgets import card, tree_with_scroll, fill_tree, page_header, separator


class DashboardPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=C_BG_MAIN, corner_radius=0)
        self.user = user
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "🏠  Главная панель",
                    f"Добро пожаловать, {self.user['full_name'].split()[0]}!")
        separator(self)

        # ── Карточки ────────────────────────────────────────
        cards_f = ctk.CTkFrame(self, fg_color="transparent")
        cards_f.pack(fill="x", padx=24, pady=(8, 12))
        for i in range(5):
            cards_f.grid_columnconfigure(i, weight=1)

        self._c = {}
        defs = [
            ("mat",   "Материалов",          "—", C_GREEN_PRIMARY,  "📦"),
            ("val",   "Стоимость склада",     "—", "#1A5276",        "💰"),
            ("low",   "Ниже нормы",           "—", C_RED,            "⚠️"),
            ("rec",   "Поступлений сегодня",  "—", "#1E8449",        "📥"),
            ("wrt",   "Списаний сегодня",     "—", "#6E2F2F",        "📤"),
        ]
        for col, (key, title, val, color, icon) in enumerate(defs):
            f = ctk.CTkFrame(cards_f, fg_color=color, corner_radius=CARD_RADIUS)
            f.grid(row=0, column=col, padx=5, sticky="ew", ipady=4)
            ctk.CTkLabel(f, text=f"{icon}  {title}",
                         font=(FONT_FAMILY, 10), text_color="white").pack(pady=(12,2), padx=14, anchor="w")
            lbl = ctk.CTkLabel(f, text=val,
                               font=(FONT_FAMILY, 22, "bold"), text_color="white")
            lbl.pack(pady=(0,12), padx=14, anchor="w")
            self._c[key] = lbl

        # ── Нижняя половина ─────────────────────────────────
        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.pack(fill="both", expand=True, padx=24, pady=(0, 16))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_columnconfigure(1, weight=1)
        bottom.grid_rowconfigure(0, weight=3)
        bottom.grid_rowconfigure(1, weight=2)

        # Последние поступления
        self._rec_frame, self._rec_tree = self._ops_panel(
            bottom, "📥  Последние поступления",
            [("Дата", 120, "center"), ("Материал", 180, "w"),
             ("Кол-во", 70, "center"), ("Ед.", 50, "center"), ("Поставщик", 130, "w")],
            row=0, col=0, padx=(0, 6),
        )
        # Последние списания
        self._wrt_frame, self._wrt_tree = self._ops_panel(
            bottom, "📤  Последние списания",
            [("Дата", 120, "center"), ("Материал", 180, "w"),
             ("Кол-во", 70, "center"), ("Ед.", 50, "center"), ("Основание", 130, "w")],
            row=0, col=1, padx=(6, 0),
        )
        # Критические остатки
        low_wrap = ctk.CTkFrame(bottom, fg_color=C_BG_CARD, corner_radius=CARD_RADIUS)
        low_wrap.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=(10, 0))

        hdr = ctk.CTkFrame(low_wrap, fg_color="transparent")
        hdr.pack(fill="x", padx=14, pady=(10, 6))
        ctk.CTkLabel(hdr, text="⚠️  Материалы ниже минимального остатка",
                     font=(FONT_FAMILY, 13, "bold"),
                     text_color=C_RED).pack(side="left")

        from ui.widgets import make_treeview
        import tkinter.ttk as ttk
        low_cols = [("Материал",160,"w"),("Категория",130,"w"),
                    ("Остаток",80,"center"),("Минимум",80,"center"),("Ед.",60,"center")]
        self._low_tree = make_treeview(low_wrap, low_cols, height=4)
        vsb = ttk.Scrollbar(low_wrap, orient="vertical", command=self._low_tree.yview)
        self._low_tree.configure(yscrollcommand=vsb.set)
        self._low_tree.pack(side="left", fill="both", expand=True, padx=(14,0), pady=(0,10))
        vsb.pack(side="right", fill="y", pady=(0,10), padx=(0,8))

    def _ops_panel(self, parent, title, cols, row, col, padx):
        wrap = ctk.CTkFrame(parent, fg_color=C_BG_CARD, corner_radius=CARD_RADIUS)
        wrap.grid(row=row, column=col, sticky="nsew", padx=padx, pady=(0, 0))

        ctk.CTkLabel(wrap, text=title, font=(FONT_FAMILY, 13, "bold"),
                     text_color=C_TEXT_MAIN).pack(anchor="w", padx=14, pady=(10, 6))

        from ui.widgets import make_treeview
        import tkinter.ttk as ttk
        tree = make_treeview(wrap, cols, height=7)
        vsb  = ttk.Scrollbar(wrap, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=vsb.set)
        tree.pack(side="left", fill="both", expand=True, padx=(14,0), pady=(0,10))
        vsb.pack(side="right", fill="y", pady=(0,10), padx=(0,8))
        return wrap, tree

    def refresh(self):
        try:
            from services.report_service import get_dashboard_stats
            s = get_dashboard_stats()
        except Exception:
            return

        self._c["mat"].configure(text=str(s["materials_count"]))
        self._c["val"].configure(text=f"{s['total_value']:,.0f} ₽")
        low = s["low_stock_count"]
        self._c["low"].configure(text=str(low))
        self._c["rec"].configure(text=str(s["receipts_today"]))
        self._c["wrt"].configure(text=str(s["writeoffs_today"]))

        # Поступления
        for item in self._rec_tree.get_children(): self._rec_tree.delete(item)
        for i, r in enumerate(s["last_receipts"]):
            dt = r["created_at"].strftime("%d.%m %H:%M") if hasattr(r["created_at"],"strftime") else str(r["created_at"])
            tag = "odd" if i%2 else "even"
            self._rec_tree.insert("","end", values=(dt, r["material"], r["quantity"], r["unit"], r.get("supplier","—")), tags=(tag,))

        # Списания
        for item in self._wrt_tree.get_children(): self._wrt_tree.delete(item)
        for i, w in enumerate(s["last_writeoffs"]):
            dt = w["created_at"].strftime("%d.%m %H:%M") if hasattr(w["created_at"],"strftime") else str(w["created_at"])
            tag = "odd" if i%2 else "even"
            self._wrt_tree.insert("","end", values=(dt, w["material"], w["quantity"], w["unit"], w.get("reason","—")), tags=(tag,))

        # Ниже нормы
        for item in self._low_tree.get_children(): self._low_tree.delete(item)
        for i, m in enumerate(s["low_list"]):
            tag = "low_odd" if i%2 else "low"
            self._low_tree.insert("","end",
                values=(m["name"],m["category"],m["quantity"],m["min_quantity"],m["unit"]),
                tags=(tag,))
