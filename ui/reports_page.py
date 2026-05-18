import customtkinter as ctk
from datetime import date, timedelta
from ui.theme import *
from ui.widgets import tree_with_scroll, page_header, separator, btn
from services.report_service import get_stock_report, get_receipts_report, get_writeoffs_report


class ReportsPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=C_BG_MAIN, corner_radius=0)
        self.user = user
        self._tab = "stock"
        self._build()
        self._load()

    def _build(self):
        page_header(self, "📊  Отчёты")
        separator(self)

        # ── Вкладки ─────────────────────────────────────────
        tab_f = ctk.CTkFrame(self, fg_color="transparent")
        tab_f.pack(fill="x", padx=24, pady=(8,0))

        self._tab_btns = {}
        tabs = [("stock","📦  Остатки"),("receipts","📥  Поступления"),("writeoffs","📤  Списания")]
        for key, label in tabs:
            b = ctk.CTkButton(tab_f, text=label, width=160,
                              fg_color=C_GREEN_ACCENT if key=="stock" else C_BG_CARD,
                              hover_color=C_GREEN_PRIMARY,
                              text_color="white" if key=="stock" else C_TEXT_MAIN,
                              border_color=C_BORDER, border_width=1,
                              corner_radius=BTN_RADIUS, height=36,
                              font=(FONT_FAMILY, 12),
                              command=lambda k=key: self._switch(k))
            b.pack(side="left", padx=(0,6))
            self._tab_btns[key] = b

        # ── Фильтр дат ───────────────────────────────────────
        self._date_f = ctk.CTkFrame(self, fg_color="transparent")

        ctk.CTkLabel(self._date_f, text="Период  с:", font=FONT_BODY,
                     text_color=C_TEXT_SECONDARY).pack(side="left")
        self._df = ctk.CTkEntry(self._date_f, width=110, height=36,
                                font=(FONT_FAMILY,12), fg_color=C_BG_CARD,
                                border_color=C_BORDER, text_color=C_TEXT_MAIN,
                                corner_radius=BTN_RADIUS, placeholder_text="ГГГГ-ММ-ДД")
        self._df.pack(side="left", padx=6)
        self._df.insert(0, str(date.today()-timedelta(days=30)))

        ctk.CTkLabel(self._date_f, text="по:", font=FONT_BODY,
                     text_color=C_TEXT_SECONDARY).pack(side="left")
        self._dt = ctk.CTkEntry(self._date_f, width=110, height=36,
                                font=(FONT_FAMILY,12), fg_color=C_BG_CARD,
                                border_color=C_BORDER, text_color=C_TEXT_MAIN,
                                corner_radius=BTN_RADIUS, placeholder_text="ГГГГ-ММ-ДД")
        self._dt.pack(side="left", padx=6)
        self._dt.insert(0, str(date.today()))

        btn(self._date_f, "🔍  Применить", self._load, width=130).pack(side="left", padx=6)
        btn(self._date_f, "Сбросить", self._reset, style="secondary", width=90).pack(side="left")

        # ── Таблица ─────────────────────────────────────────
        self._tbl_wrap = ctk.CTkFrame(self, fg_color="transparent")
        self._tbl_wrap.pack(fill="both", expand=True, padx=24, pady=(8,8))
        self._tbl_wrap.grid_rowconfigure(0, weight=1)
        self._tbl_wrap.grid_columnconfigure(0, weight=1)

        self._frame = None
        self._tree  = None

        self._status = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=C_TEXT_MUTED)
        self._status.pack(anchor="w", padx=24, pady=(0,8))

    def _switch(self, key):
        self._tab = key
        for k, b in self._tab_btns.items():
            b.configure(
                fg_color=C_GREEN_ACCENT if k==key else C_BG_CARD,
                text_color="white" if k==key else C_TEXT_MAIN,
            )
        if key=="stock":
            self._date_f.pack_forget()
        else:
            self._date_f.pack(fill="x", padx=24, pady=(8,0),
                              after=list(self.children.values())[3])
        self._load()

    def _reset(self):
        self._df.delete(0,"end"); self._df.insert(0, str(date.today()-timedelta(days=30)))
        self._dt.delete(0,"end"); self._dt.insert(0, str(date.today()))
        self._load()

    def _rebuild_tree(self, cols):
        if self._frame:
            self._frame.destroy()
        self._frame, self._tree = tree_with_scroll(self._tbl_wrap, cols, height=24)
        self._frame.grid(row=0, column=0, sticky="nsew")

    def _load(self):
        tab = self._tab
        if tab == "stock":
            cols = [("Материал",220,"w"),("Категория",130,"w"),("Ед.",55,"center"),
                    ("Остаток",85,"center"),("Минимум",85,"center"),
                    ("Цена",80,"center"),("Сумма",100,"center"),("Статус",110,"center")]
            self._rebuild_tree(cols)
            rows = get_stock_report()
            total = 0
            for i, r in enumerate(rows):
                is_low = r["status"]=="Ниже нормы"
                tag = ("low_odd" if i%2 else "low") if is_low else ("odd" if i%2 else "even")
                tv = float(r["total_value"] or 0)
                total += tv
                self._tree.insert("","end", tags=(tag,), values=(
                    r["name"],r["category"],r["unit"],
                    r["quantity"],r["min_quantity"],
                    f"{float(r['price']):.2f} ₽",
                    f"{tv:.2f} ₽", r["status"],
                ))
            self._status.configure(
                text=f"Материалов: {len(rows)}   |   Общая стоимость склада: {total:,.2f} ₽")

        elif tab == "receipts":
            cols = [("ID",45,"center"),("Дата",130,"center"),("Материал",200,"w"),
                    ("Ед.",50,"center"),("Кол-во",75,"center"),("Цена",80,"center"),
                    ("Сумма",95,"center"),("Поставщик",140,"w"),("№ докум.",110,"center"),
                    ("Кто добавил",140,"w")]
            self._rebuild_tree(cols)
            df = self._df.get().strip() or None
            dt = self._dt.get().strip() or None
            rows = get_receipts_report(df, dt)
            total = 0
            for i, r in enumerate(rows):
                d = r["created_at"].strftime("%d.%m.%Y %H:%M") if hasattr(r["created_at"],"strftime") else str(r["created_at"])
                t = float(r.get("total") or 0)
                total += t
                tag = "odd" if i%2 else "even"
                self._tree.insert("","end", iid=str(r["id"]), tags=(tag,), values=(
                    r["id"],d,r["material"],r["unit"],
                    r["quantity"],f"{float(r['price']):.2f} ₽",
                    f"{t:.2f} ₽",
                    r.get("supplier") or "—",
                    r.get("document_number") or "—",
                    r.get("created_by") or "—",
                ))
            self._status.configure(text=f"Записей: {len(rows)}   |   Итого: {total:,.2f} ₽")

        else:
            cols = [("ID",45,"center"),("Дата",130,"center"),("Материал",200,"w"),
                    ("Ед.",50,"center"),("Кол-во",75,"center"),
                    ("Основание",200,"w"),("№ докум.",110,"center"),("Кто добавил",140,"w")]
            self._rebuild_tree(cols)
            df = self._df.get().strip() or None
            dt = self._dt.get().strip() or None
            rows = get_writeoffs_report(df, dt)
            for i, w in enumerate(rows):
                d = w["created_at"].strftime("%d.%m.%Y %H:%M") if hasattr(w["created_at"],"strftime") else str(w["created_at"])
                tag = "odd" if i%2 else "even"
                self._tree.insert("","end", iid=str(w["id"]), tags=(tag,), values=(
                    w["id"],d,w["material"],w["unit"],
                    w["quantity"],w.get("reason") or "—",
                    w.get("document_number") or "—",
                    w.get("created_by") or "—",
                ))
            self._status.configure(text=f"Записей: {len(rows)}")
