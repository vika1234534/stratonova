"""Переиспользуемые компоненты интерфейса."""
import customtkinter as ctk
from tkinter import ttk
from ui.theme import *


def make_treeview(parent, columns: list[tuple], height=16) -> ttk.Treeview:
    """columns = [(name, width, anchor), ...]"""
    style = ttk.Style()
    style.theme_use("clam")
    style.configure("Corp.Treeview",
        background=C_BG_CARD,
        foreground=C_TEXT_MAIN,
        fieldbackground=C_BG_CARD,
        rowheight=30,
        font=(FONT_FAMILY, 10),
        borderwidth=0,
    )
    style.configure("Corp.Treeview.Heading",
        background=C_GREEN_PRIMARY,
        foreground="white",
        font=(FONT_FAMILY, 10, "bold"),
        relief="flat",
        borderwidth=0,
    )
    style.map("Corp.Treeview",
        background=[("selected", C_GREEN_ACCENT)],
        foreground=[("selected", "white")],
    )
    style.map("Corp.Treeview.Heading",
        background=[("active", C_GREEN_ACCENT)],
    )

    col_ids = [c[0] for c in columns]
    tree = ttk.Treeview(parent, columns=col_ids, show="headings",
                        style="Corp.Treeview", height=height)
    for name, width, anchor in columns:
        tree.heading(name, text=name)
        tree.column(name, width=width, anchor=anchor, stretch=False)

    tree.tag_configure("odd",  background="#F7FAF8")
    tree.tag_configure("even", background=C_BG_CARD)
    tree.tag_configure("low",  background="#FDECEA", foreground=C_RED)
    tree.tag_configure("low_odd", background="#FAE5E2", foreground=C_RED)

    return tree


def tree_with_scroll(parent, columns, height=16):
    """Возвращает (frame, tree)."""
    frame = ctk.CTkFrame(parent, fg_color=C_BG_CARD, corner_radius=CARD_RADIUS)
    tree  = make_treeview(frame, columns, height=height)
    vsb   = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
    hsb   = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
    tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)
    tree.grid(row=0, column=0, sticky="nsew")
    vsb.grid (row=0, column=1, sticky="ns")
    hsb.grid (row=1, column=0, sticky="ew")
    frame.grid_rowconfigure(0, weight=1)
    frame.grid_columnconfigure(0, weight=1)
    return frame, tree


def fill_tree(tree: ttk.Treeview, rows: list, transform=None):
    """Очистить и заполнить Treeview. transform(row)->tuple значений."""
    for item in tree.get_children():
        tree.delete(item)
    for i, row in enumerate(rows):
        vals = transform(row) if transform else tuple(row.values())
        tag  = "odd" if i % 2 else "even"
        tree.insert("", "end", iid=str(row.get("id", i)), values=vals, tags=(tag,))


def card(parent, title: str, value: str, color: str, icon: str = "") -> ctk.CTkLabel:
    """Карточка статистики. Возвращает label значения."""
    f = ctk.CTkFrame(parent, fg_color=color, corner_radius=CARD_RADIUS)
    ctk.CTkLabel(f, text=f"{icon}  {title}" if icon else title,
                 font=(FONT_FAMILY, 11), text_color="white").pack(pady=(14,2), padx=16, anchor="w")
    lbl = ctk.CTkLabel(f, text=value,
                       font=(FONT_FAMILY, 24, "bold"), text_color="white")
    lbl.pack(pady=(0,14), padx=16, anchor="w")
    return lbl


def page_header(parent, title: str, subtitle: str = ""):
    f = ctk.CTkFrame(parent, fg_color="transparent")
    f.pack(fill="x", padx=24, pady=(20, 4))
    ctk.CTkLabel(f, text=title, font=(FONT_FAMILY, 20, "bold"),
                 text_color=C_TEXT_MAIN).pack(side="left")
    if subtitle:
        ctk.CTkLabel(f, text=subtitle, font=(FONT_FAMILY, 11),
                     text_color=C_TEXT_MUTED).pack(side="left", padx=(12,0), pady=(6,0))
    return f


def separator(parent):
    ctk.CTkFrame(parent, height=1, fg_color=C_BORDER).pack(fill="x", padx=24, pady=4)


def btn(parent, text, command, style="primary", **kw):
    styles = {"primary": BTN_PRIMARY, "secondary": BTN_SECONDARY, "danger": BTN_DANGER}
    cfg = {**styles.get(style, BTN_PRIMARY), **kw}
    return ctk.CTkButton(parent, text=text, command=command, **cfg)


class Toast(ctk.CTkToplevel):
    """Всплывающее уведомление."""
    def __init__(self, master, message: str, color: str = C_GREEN_ACCENT, duration: int = 2500):
        super().__init__(master)
        self.overrideredirect(True)
        self.attributes("-topmost", True)
        self.configure(fg_color=color)
        ctk.CTkLabel(self, text=message, text_color="white",
                     font=(FONT_FAMILY, 12), padx=20, pady=12).pack()
        # Позиционирование
        self.update_idletasks()
        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        w  = self.winfo_width()
        h  = self.winfo_height()
        self.geometry(f"+{sw-w-30}+{sh-h-60}")
        self.after(duration, self.destroy)


def show_toast(master, message: str, ok: bool = True):
    Toast(master, ("✓  " if ok else "✗  ") + message,
          color=C_GREEN_ACCENT if ok else C_RED)


class ConfirmDialog(ctk.CTkToplevel):
    """Диалог подтверждения. result = True/False."""
    def __init__(self, master, title="Подтверждение", message=""):
        super().__init__(master)
        self.title(title)
        self.geometry("360x160")
        self.resizable(False, False)
        self.grab_set()
        self.result = False
        ctk.CTkLabel(self, text=message, font=(FONT_FAMILY, 12),
                     wraplength=320).pack(pady=24, padx=20)
        row = ctk.CTkFrame(self, fg_color="transparent")
        row.pack()
        ctk.CTkButton(row, text="Да", width=100, **BTN_DANGER,
                      command=self._yes).pack(side="left", padx=8)
        ctk.CTkButton(row, text="Отмена", width=100, **BTN_SECONDARY,
                      command=self.destroy).pack(side="left", padx=8)
        self.wait_window()

    def _yes(self):
        self.result = True
        self.destroy()
