import customtkinter as ctk, subprocess, sys, os
from tkinter import messagebox
from ui.theme import *
from ui.widgets import tree_with_scroll, page_header, separator, btn, show_toast
from services.material_service import get_materials
from services.stock_service import add_receipt, get_receipts, get_receipt_by_id
from services.log_service import log


class ReceiptsPage(ctk.CTkFrame):
    def __init__(self, master, user):
        super().__init__(master, fg_color=C_BG_MAIN, corner_radius=0)
        self.user = user
        self._build()
        self.refresh()

    def _build(self):
        page_header(self, "📥  Поступление материалов")
        separator(self)

        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.pack(fill="x", padx=24, pady=(8,10))
        btn(toolbar, "➕  Добавить поступление", self._add, width=190).pack(side="left", padx=(0,6))
        btn(toolbar, "🖨  Печать накладной",     self._pdf, style="secondary", width=160).pack(side="left", padx=4)
        btn(toolbar, "🔄", self.refresh, style="secondary", width=44).pack(side="right")

        cols = [
            ("ID",        45, "center"),
            ("Дата",     135, "center"),
            ("Материал", 210, "w"),
            ("Ед.",       50, "center"),
            ("Кол-во",    75, "center"),
            ("Цена",      85, "center"),
            ("Сумма",     95, "center"),
            ("Поставщик",150, "w"),
            ("№ докум.", 110, "center"),
            ("Кто добавил",140,"w"),
        ]
        frame, self._tree = tree_with_scroll(self, cols, height=22)
        frame.pack(fill="both", expand=True, padx=24, pady=(0,8))

        self._status = ctk.CTkLabel(self, text="", font=FONT_SMALL, text_color=C_TEXT_MUTED)
        self._status.pack(anchor="w", padx=24, pady=(0,8))

    def refresh(self):
        rows = get_receipts()
        for item in self._tree.get_children(): self._tree.delete(item)
        total_sum = 0
        for i, r in enumerate(rows):
            dt = r["created_at"].strftime("%d.%m.%Y %H:%M") if hasattr(r["created_at"],"strftime") else str(r["created_at"])
            total = float(r.get("total") or 0)
            total_sum += total
            tag = "odd" if i%2 else "even"
            self._tree.insert("","end", iid=str(r["id"]), tags=(tag,), values=(
                r["id"], dt, r["material"], r["unit"],
                r["quantity"], f"{float(r['price']):.2f} ₽",
                f"{total:.2f} ₽",
                r.get("supplier") or "—",
                r.get("document_number") or "—",
                r.get("created_by") or "—",
            ))
        self._status.configure(text=f"Записей: {len(rows)}   |   Итого: {total_sum:,.2f} ₽")

    def _sel(self):
        s = self._tree.selection()
        if not s:
            messagebox.showwarning("Выбор","Выберите запись в списке"); return None
        return int(s[0])

    def _add(self):
        dlg = ctk.CTkToplevel(self)
        dlg.title("Добавить поступление")
        dlg.geometry("520x540")
        dlg.resizable(False, False)
        dlg.configure(fg_color=C_BG_MAIN)
        dlg.grab_set()

        ctk.CTkLabel(dlg, text="📥  Новое поступление",
                     font=(FONT_FAMILY,16,"bold"), text_color=C_TEXT_MAIN).pack(pady=(20,4), padx=24, anchor="w")
        ctk.CTkFrame(dlg, height=1, fg_color=C_BORDER).pack(fill="x", padx=24, pady=(0,16))

        form = ctk.CTkFrame(dlg, fg_color="transparent")
        form.pack(fill="x", padx=24)
        form.grid_columnconfigure(0, weight=1)
        form.grid_columnconfigure(1, weight=1)

        mats = get_materials()
        mat_names = [f"{m['name']}  ({m['unit']})" for m in mats]

        def lbl(text, row, col=0, span=2):
            ctk.CTkLabel(form, text=text, font=(FONT_FAMILY,11,"bold"),
                         text_color=C_TEXT_MAIN).grid(row=row*2, column=col, columnspan=span,
                                                       sticky="w", pady=(8,2))
        def entry(row, col=0, span=2, placeholder=""):
            e = ctk.CTkEntry(form, height=38, font=(FONT_FAMILY,12),
                             fg_color=C_BG_CARD, border_color=C_BORDER,
                             text_color=C_TEXT_MAIN, corner_radius=BTN_RADIUS,
                             placeholder_text=placeholder)
            e.grid(row=row*2+1, column=col, columnspan=span, sticky="ew",
                   padx=(0,6) if col==0 and span==1 else (6,0) if col==1 else 0)
            return e

        lbl("Материал *", 0)
        mat_cb = ctk.CTkComboBox(form, values=mat_names, height=38,
                                  font=(FONT_FAMILY,12), fg_color=C_BG_CARD,
                                  border_color=C_BORDER, button_color=C_GREEN_ACCENT,
                                  dropdown_fg_color=C_BG_CARD, corner_radius=BTN_RADIUS)
        mat_cb.grid(row=1, column=0, columnspan=2, sticky="ew")

        lbl("Количество *", 1, col=0, span=1)
        lbl("Цена за единицу (₽)", 1, col=1, span=1)
        e_qty   = entry(1, col=0, span=1, placeholder="0")
        e_price = entry(1, col=1, span=1, placeholder="0.00")

        lbl("Поставщик", 2)
        e_sup = entry(2, placeholder="Название поставщика")

        lbl("Номер документа", 3, col=0, span=1)
        lbl("Примечание", 3, col=1, span=1)
        e_doc  = entry(3, col=0, span=1, placeholder="№")
        e_note = entry(3, col=1, span=1)

        err_lbl = ctk.CTkLabel(dlg, text="", font=(FONT_FAMILY,11), text_color=C_RED)
        err_lbl.pack(pady=(8,0))

        def save():
            mat_n = mat_cb.get()
            if not mat_n or mat_n not in mat_names:
                err_lbl.configure(text="Выберите материал"); return
            mat = mats[mat_names.index(mat_n)]
            try:
                qty = int(e_qty.get() or 0)
                if qty <= 0: raise ValueError
            except ValueError:
                err_lbl.configure(text="Введите корректное количество (целое число)"); return
            try:
                price = float(e_price.get() or 0)
            except ValueError:
                err_lbl.configure(text="Введите корректную цену"); return
            try:
                rid = add_receipt(mat["id"], qty, price,
                                  e_sup.get(), e_doc.get(), e_note.get(), self.user["id"])
                log(self.user["id"], "RECEIPT_ADD",
                    f"Приход ID={rid}: {mat['name']} x{qty}")
                dlg.destroy()
                self.refresh()
                show_toast(self, f"Поступление добавлено: {mat['name']} × {qty}")
            except Exception as e:
                err_lbl.configure(text=str(e))

        ctk.CTkFrame(dlg, height=1, fg_color=C_BORDER).pack(fill="x", padx=24, pady=(12,12))
        row_b = ctk.CTkFrame(dlg, fg_color="transparent")
        row_b.pack(padx=24)
        btn(row_b, "💾  Сохранить", save, width=140).pack(side="left", padx=6)
        btn(row_b, "Отмена", dlg.destroy, style="secondary", width=100).pack(side="left", padx=6)

    def _pdf(self):
        rid = self._sel()
        if not rid: return
        try:
            r = get_receipt_by_id(rid)
            from reports.pdf_generator import generate_receipt_pdf
            path = generate_receipt_pdf(r)
            show_toast(self, "PDF-накладная сформирована")
            if   sys.platform=="win32": os.startfile(path)
            elif sys.platform=="darwin": subprocess.run(["open",path])
            else: subprocess.run(["xdg-open",path])
        except Exception as e:
            messagebox.showerror("Ошибка PDF", str(e))
