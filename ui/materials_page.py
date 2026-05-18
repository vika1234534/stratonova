import customtkinter as ctk
from tkinter import messagebox, simpledialog
from ui.theme import *
from ui.widgets import (tree_with_scroll, fill_tree, page_header,
                        separator, btn, show_toast, ConfirmDialog)
from services.auth_service import is_admin
from services.material_service import (
    get_materials, get_categories, get_units,
    add_material, update_material, delete_material,
    set_min_quantity, get_material_by_id,
)
from services.log_service import log


class MaterialsPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=C_BG_MAIN, corner_radius=0)
        self.user = user
        self._cats = []
        self._units = []
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "📦  Справочник материалов")
        separator(self)

        # ── Панель инструментов ──────────────────────────────
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(8, 10))

        # Поиск
        search_f = ctk.CTkFrame(toolbar, fg_color=C_BG_CARD,
                                corner_radius=BTN_RADIUS, border_width=1,
                                border_color=C_BORDER)
        search_f.pack(side="left")
        ctk.CTkLabel(search_f, text="🔍", font=(FONT_FAMILY, 13)).pack(side="left", padx=(10,2))
        self._search = ctk.CTkEntry(search_f, width=200, height=36,
                                    placeholder_text="Поиск по названию…",
                                    font=(FONT_FAMILY, 12),
                                    fg_color="transparent",
                                    border_width=0,
                                    text_color=C_TEXT_MAIN)
        self._search.pack(side="left", padx=(0,8))
        self._search.bind("<KeyRelease>", lambda e: self.refresh())

        # Категория
        ctk.CTkLabel(toolbar, text="Категория:", font=FONT_BODY,
                     text_color=C_TEXT_SECONDARY).pack(side="left", padx=(16,6))
        self._cat_var = ctk.StringVar(value="Все")
        self._cat_cb  = ctk.CTkComboBox(toolbar, variable=self._cat_var, width=180,
                                         height=36, font=(FONT_FAMILY, 12),
                                         fg_color=C_BG_CARD,
                                         border_color=C_BORDER,
                                         button_color=C_GREEN_ACCENT,
                                         dropdown_fg_color=C_BG_CARD,
                                         command=lambda _: self.refresh())
        self._cat_cb.pack(side="left")

        # Кнопки
        btn_f = ctk.CTkFrame(toolbar, fg_color="transparent")
        btn_f.pack(side="right")

        btn(btn_f, "➕  Добавить", self._add, width=130).pack(side="left", padx=4)
        btn(btn_f, "✏️  Изменить", self._edit, style="secondary", width=120).pack(side="left", padx=4)
        btn(btn_f, "🗑  Удалить",  self._delete, style="danger",    width=110).pack(side="left", padx=4)
        if is_admin(self.user):
            btn(btn_f, "⚙️  Мин. остаток", self._set_min,
                style="secondary", width=140).pack(side="left", padx=4)
        btn(btn_f, "🔄", self.refresh, style="secondary", width=44).pack(side="left", padx=4)

        # ── Таблица ──────────────────────────────────────────
        cols = [
            ("ID",        40,  "center"),
            ("Название",  240, "w"),
            ("Категория", 140, "w"),
            ("Ед.",        50, "center"),
            ("Остаток",    80, "center"),
            ("Минимум",    80, "center"),
            ("Цена",       90, "center"),
            ("Статус",    110, "center"),
        ]
        frame, self._tree = tree_with_scroll(self, cols, height=20)
        frame.pack(fill="both", expand=True, padx=24, pady=(0, 8))
        self._tree.bind("<Double-1>", lambda e: self._edit())

        # Статусбар
        self._status = ctk.CTkLabel(self, text="", font=FONT_SMALL,
                                    text_color=C_TEXT_MUTED)
        self._status.pack(anchor="w", padx=24, pady=(0, 8))

    def refresh(self):
        self._cats  = get_categories()
        self._units = get_units()
        cat_names   = ["Все"] + [c["name"] for c in self._cats]
        self._cat_cb.configure(values=cat_names)

        search   = self._search.get().strip()
        cat_name = self._cat_var.get()
        cat_id   = None
        if cat_name != "Все":
            found = [c for c in self._cats if c["name"] == cat_name]
            if found: cat_id = found[0]["id"]

        rows = get_materials(search=search, category_id=cat_id)

        for item in self._tree.get_children():
            self._tree.delete(item)

        low = 0
        for i, r in enumerate(rows):
            is_low = bool(r["low_stock"])
            if is_low: low += 1
            status = "⚠️ Ниже нормы" if is_low else "✅ В норме"
            if is_low:
                tag = "low_odd" if i%2 else "low"
            else:
                tag = "odd" if i%2 else "even"
            self._tree.insert("","end", iid=str(r["id"]), tags=(tag,), values=(
                r["id"], r["name"], r["category"], r["unit"],
                r["quantity"], r["min_quantity"],
                f"{float(r['price']):.2f} ₽", status,
            ))
        total = len(rows)
        self._status.configure(
            text=f"Всего: {total}   |   Ниже нормы: {low}",
            text_color=C_RED if low else C_TEXT_MUTED,
        )

    def _sel(self):
        s = self._tree.selection()
        if not s:
            messagebox.showwarning("Выбор", "Выберите материал из списка")
            return None
        return int(s[0])

    # ── Форма добавления / редактирования ───────────────────
    def _form(self, title, initial=None):
        dlg = ctk.CTkToplevel(self)
        dlg.title(title)
        dlg.geometry("500x520")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C_BG_MAIN)
        dlg.grab_set()

        # Заголовок
        ctk.CTkLabel(dlg, text=title,
                     font=(FONT_FAMILY, 16, "bold"),
                     text_color=C_TEXT_MAIN).pack(pady=(20,4), padx=24, anchor="w")
        ctk.CTkFrame(dlg, height=1, fg_color=C_BORDER).pack(fill="x", padx=24, pady=(0,16))

        form = ctk.CTkFrame(dlg, fg_color="transparent")
        form.pack(fill="x", padx=24)
        fields = {}

        def field(label, key, placeholder="", row=0, col=0, span=2):
            ctk.CTkLabel(form, text=label, font=(FONT_FAMILY,11,"bold"),
                         text_color=C_TEXT_MAIN).grid(row=row*2, column=col, columnspan=span,
                                                       sticky="w", pady=(8,2))
            e = ctk.CTkEntry(form, placeholder_text=placeholder,
                             height=38, font=(FONT_FAMILY,12),
                             fg_color=C_BG_CARD, border_color=C_BORDER,
                             text_color=C_TEXT_MAIN, corner_radius=BTN_RADIUS)
            e.grid(row=row*2+1, column=col, columnspan=span, sticky="ew",
                   padx=(0,8) if col==0 and span==1 else (8,0) if col==1 else 0)
            fields[key] = e
            return e

        def combo(label, key, values, row=0, col=0):
            ctk.CTkLabel(form, text=label, font=(FONT_FAMILY,11,"bold"),
                         text_color=C_TEXT_MAIN).grid(row=row*2, column=col, sticky="w", pady=(8,2))
            c = ctk.CTkComboBox(form, values=values, height=38,
                                font=(FONT_FAMILY,12),
                                fg_color=C_BG_CARD, border_color=C_BORDER,
                                button_color=C_GREEN_ACCENT,
                                dropdown_fg_color=C_BG_CARD,
                                corner_radius=BTN_RADIUS)
            c.grid(row=row*2+1, column=col, sticky="ew",
                   padx=(0,8) if col==0 else (8,0))
            fields[key] = c
            return c

        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        field("Название материала *", "name", "Введите название", row=0, span=2)
        if initial: fields["name"].insert(0, initial.get("name",""))

        cat_names  = [c["name"] for c in self._cats]
        unit_names = [u["name"] for u in self._units]
        combo("Категория *",         "category", cat_names,  row=1, col=0)
        combo("Единица измерения *", "unit",     unit_names, row=1, col=1)
        if initial:
            fields["category"].set(initial.get("category", cat_names[0] if cat_names else ""))
            fields["unit"].set(initial.get("unit", unit_names[0] if unit_names else ""))

        if not initial:
            field("Начальное количество", "qty", "0", row=2, col=0, span=1)
            fields["qty"].insert(0, "0")

        if is_admin(self.user):
            field("Мин. остаток", "min_qty", "0", row=2, col=1 if not initial else 0, span=1)
            if initial: fields["min_qty"].insert(0, str(initial.get("min_quantity",0)))

        field("Цена за единицу (₽)", "price", "0.00",
              row=3 if (not initial or is_admin(self.user)) else 2,
              col=1 if is_admin(self.user) and initial else 0,
              span=1 if (is_admin(self.user) and initial) else 2)
        if initial: fields["price"].insert(0, str(initial.get("price",0)))

        result = {}

        def save():
            name = fields["name"].get().strip()
            if not name:
                messagebox.showwarning("Ошибка","Введите название",parent=dlg); return
            cat_n = fields["category"].get()
            cat = next((c for c in self._cats if c["name"]==cat_n), None)
            if not cat:
                messagebox.showwarning("Ошибка","Выберите категорию",parent=dlg); return
            unit_n = fields["unit"].get()
            unit = next((u for u in self._units if u["name"]==unit_n), None)
            if not unit:
                messagebox.showwarning("Ошибка","Выберите единицу",parent=dlg); return
            try:
                qty     = int(fields["qty"].get() or 0) if "qty" in fields else 0
                min_qty = int(fields["min_qty"].get() or 0) if "min_qty" in fields else (initial.get("min_quantity",0) if initial else 0)
                price   = float(fields["price"].get() or 0)
            except ValueError:
                messagebox.showwarning("Ошибка","Проверьте числовые поля",parent=dlg); return

            result.update(dict(name=name, category_id=cat["id"], unit_id=unit["id"],
                               quantity=qty, min_quantity=min_qty, price=price))
            dlg.destroy()

        # Кнопки формы
        ctk.CTkFrame(dlg, height=1, fg_color=C_BORDER).pack(fill="x", padx=24, pady=(16,12))
        row_btns = ctk.CTkFrame(dlg, fg_color="transparent")
        row_btns.pack(padx=24)
        btn(row_btns, "💾  Сохранить", save, width=140).pack(side="left", padx=6)
        btn(row_btns, "Отмена", dlg.destroy, style="secondary", width=100).pack(side="left", padx=6)

        dlg.wait_window()
        return result if result else None

    def _add(self):
        data = self._form("Добавить материал")
        if not data: return
        try:
            add_material(data["name"], data["category_id"], data["unit_id"],
                         data["quantity"], data["min_quantity"], data["price"])
            log(self.user["id"], "MATERIAL_ADD", f"Добавлен: {data['name']}")
            self.refresh()
            show_toast(self, f"Материал «{data['name']}» добавлен")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _edit(self):
        mid = self._sel()
        if not mid: return
        mat = get_material_by_id(mid)
        if not mat: return
        data = self._form("Изменить материал", initial=mat)
        if not data: return
        try:
            update_material(mid, data["name"], data["category_id"], data["unit_id"],
                            data["min_quantity"], data["price"])
            log(self.user["id"], "MATERIAL_EDIT", f"Изменён: {data['name']}")
            self.refresh()
            show_toast(self, "Материал обновлён")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _delete(self):
        mid = self._sel()
        if not mid: return
        d = ConfirmDialog(self, "Удаление", "Удалить выбранный материал?")
        if not d.result: return
        try:
            name = self._tree.item(str(mid), "values")[1]
            delete_material(mid)
            log(self.user["id"], "MATERIAL_DEL", f"Удалён: {name}")
            self.refresh()
            show_toast(self, "Материал удалён", ok=False)
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))

    def _set_min(self):
        mid = self._sel()
        if not mid: return
        val = simpledialog.askinteger("Мин. остаток",
                                      "Введите новый минимальный остаток:",
                                      minvalue=0, parent=self)
        if val is None: return
        try:
            set_min_quantity(mid, val)
            log(self.user["id"], "MATERIAL_MIN", f"ID={mid} новый мин={val}")
            self.refresh()
            show_toast(self, f"Минимальный остаток: {val}")
        except Exception as e:
            messagebox.showerror("Ошибка", str(e))
