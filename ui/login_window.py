"""
login_window.py — Premium корпоративный стиль
Левая панель: тёмная с брендингом
Правая панель: белая чистая форма
"""
import tkinter as tk
import customtkinter as ctk
from ui.theme import *


class LoginWindow(ctk.CTkToplevel):
    def __init__(self, master, on_success):
        super().__init__(master)
        self.on_success = on_success
        self.title("Система учёта ресурсов")
        self.geometry("920x580")
        self.resizable(False, False)
        self.grab_set()
        self.configure(fg_color="#FFFFFF")
        self._build()

    def _build(self):
        # ════════════════════════════════════════
        # ЛЕВАЯ ПАНЕЛЬ — тёмная, брендинг
        # ════════════════════════════════════════
        left = ctk.CTkFrame(self,
                            fg_color="#1B3A2D",
                            width=380,
                            corner_radius=0)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Верхняя зелёная линия-акцент
        accent = ctk.CTkFrame(left, height=4,
                              fg_color="#34C472",
                              corner_radius=0)
        accent.pack(fill="x", side="top")

        # Контент по центру левой панели
        left_inner = ctk.CTkFrame(left, fg_color="transparent")
        left_inner.place(relx=0.5, rely=0.5, anchor="center")

        # Логотип
        logo_bg = ctk.CTkFrame(left_inner,
                               fg_color="#243F30",
                               corner_radius=18,
                               width=76, height=76,
                               border_width=1,
                               border_color="#34C472")
        logo_bg.pack(pady=(0, 20))
        logo_bg.pack_propagate(False)
        ctk.CTkLabel(logo_bg, text="ТКН",
                     font=("Segoe UI", 24, "bold"),
                     text_color="#34C472").place(
            relx=0.5, rely=0.5, anchor="center")

        # Название
        ctk.CTkLabel(left_inner,
                     text="ТК «Новочебоксарский»",
                     font=("Segoe UI", 18, "bold"),
                     text_color="#FFFFFF").pack(pady=(0, 6))

        ctk.CTkLabel(left_inner,
                     text="Система учёта материальных\nресурсов склада",
                     font=("Segoe UI", 12),
                     text_color="#6B9E82",
                     justify="center").pack(pady=(0, 32))

        # Разделитель
        ctk.CTkFrame(left_inner, height=1,
                     fg_color="#243F30",
                     width=260).pack(pady=(0, 24))

        # Возможности
        for text in [
            "Учёт поступлений и списаний",
            "Контроль складских остатков",
            "Печать накладных и актов PDF",
            "Аналитика и журнал событий",
        ]:
            row = ctk.CTkFrame(left_inner, fg_color="transparent")
            row.pack(fill="x", pady=6)

            dot = ctk.CTkFrame(row,
                               fg_color="#34C472",
                               width=6, height=6,
                               corner_radius=3)
            dot.pack(side="left", padx=(0, 12))
            dot.pack_propagate(False)

            ctk.CTkLabel(row, text=text,
                         font=("Segoe UI", 12),
                         text_color="#8BB89E",
                         anchor="w").pack(side="left")

        # Версия внизу
        ctk.CTkLabel(left,
                     text="© 2026  ООО ТК «Новочебоксарский»",
                     font=("Segoe UI", 9),
                     text_color="#2D5A3D").pack(
            side="bottom", pady=16)

        # ════════════════════════════════════════
        # ПРАВАЯ ПАНЕЛЬ — белая, форма
        # ════════════════════════════════════════
        right = ctk.CTkFrame(self,
                             fg_color="#F8FAF9",
                             corner_radius=0)
        right.pack(side="left", fill="both", expand=True)

        form = ctk.CTkFrame(right, fg_color="transparent")
        form.place(relx=0.5, rely=0.5, anchor="center")

        # Заголовок
        ctk.CTkLabel(form,
                     text="Вход в систему",
                     font=("Segoe UI", 26, "bold"),
                     text_color="#1B3A2D").pack(pady=(0, 6))

        ctk.CTkLabel(form,
                     text="Авторизация в корпоративной системе учёта",
                     font=("Segoe UI", 11),
                     text_color="#8FA89A").pack(pady=(0, 36))

        # ── Поле логина ──────────────────────────────────────
        user_frame = ctk.CTkFrame(form,
                                  fg_color="#FFFFFF",
                                  corner_radius=12,
                                  border_width=1,
                                  border_color="#DDE8E2",
                                  width=340, height=52)
        user_frame.pack(pady=(0, 14))
        user_frame.pack_propagate(False)

        icon_u = ctk.CTkLabel(user_frame, text="👤",
                              font=("Segoe UI", 15),
                              width=44)
        icon_u.pack(side="left", padx=(12, 0))

        self.e_user = ctk.CTkEntry(user_frame,
                                   placeholder_text="Введите логин",
                                   placeholder_text_color="#B0C4B8",
                                   font=("Segoe UI", 13),
                                   fg_color="transparent",
                                   border_width=0,
                                   text_color="#1B3A2D",
                                   width=270)
        self.e_user.pack(side="left", fill="y", pady=4)

        # Focus border effect
        def focus_in_u(e):
            user_frame.configure(border_color="#34C472")
        def focus_out_u(e):
            user_frame.configure(border_color="#DDE8E2")
        self.e_user.bind("<FocusIn>",  focus_in_u)
        self.e_user.bind("<FocusOut>", focus_out_u)

        # ── Поле пароля ──────────────────────────────────────
        pass_frame = ctk.CTkFrame(form,
                                  fg_color="#FFFFFF",
                                  corner_radius=12,
                                  border_width=1,
                                  border_color="#DDE8E2",
                                  width=340, height=52)
        pass_frame.pack(pady=(0, 8))
        pass_frame.pack_propagate(False)

        icon_p = ctk.CTkLabel(pass_frame, text="🔒",
                              font=("Segoe UI", 15),
                              width=44)
        icon_p.pack(side="left", padx=(12, 0))

        self.e_pass = ctk.CTkEntry(pass_frame,
                                   placeholder_text="Введите пароль",
                                   placeholder_text_color="#B0C4B8",
                                   show="●",
                                   font=("Segoe UI", 13),
                                   fg_color="transparent",
                                   border_width=0,
                                   text_color="#1B3A2D",
                                   width=270)
        self.e_pass.pack(side="left", fill="y", pady=4)
        self.e_pass.bind("<Return>", lambda e: self._login())

        def focus_in_p(e):
            pass_frame.configure(border_color="#34C472")
        def focus_out_p(e):
            pass_frame.configure(border_color="#DDE8E2")
        self.e_pass.bind("<FocusIn>",  focus_in_p)
        self.e_pass.bind("<FocusOut>", focus_out_p)

        # ── Ошибка ───────────────────────────────────────────
        self.lbl_err = ctk.CTkLabel(form,
                                    text="",
                                    font=("Segoe UI", 11),
                                    text_color="#E05252",
                                    wraplength=340)
        self.lbl_err.pack(pady=(4, 10))

        # ── Кнопка входа ─────────────────────────────────────
        self.btn_login = ctk.CTkButton(
            form,
            text="Войти в систему",
            width=340, height=50,
            fg_color="#1B3A2D",
            hover_color="#243F30",
            text_color="#FFFFFF",
            font=("Segoe UI", 14, "bold"),
            corner_radius=12,
            command=self._login,
        )
        self.btn_login.pack()

        # Hover
        def btn_enter(e):
            self.btn_login.configure(fg_color="#34C472",
                                     text_color="#1B3A2D")
        def btn_leave(e):
            self.btn_login.configure(fg_color="#1B3A2D",
                                     text_color="#FFFFFF")
        self.btn_login.bind("<Enter>", btn_enter)
        self.btn_login.bind("<Leave>", btn_leave)

        # Нижняя подпись
        ctk.CTkLabel(form,
                     text="Складской модуль  •  v2.0",
                     font=("Segoe UI", 9),
                     text_color="#C0D4C8").pack(pady=(20, 0))

    # ── Авторизация ──────────────────────────────────────────
    def _login(self):
        u = self.e_user.get().strip()
        p = self.e_pass.get()
        self.lbl_err.configure(text="")

        if not u or not p:
            self.lbl_err.configure(text="Заполните все поля")
            return

        self.btn_login.configure(text="Проверка...", state="disabled")
        self.update()

        try:
            from services.auth_service import login
            user = login(u, p)
        except Exception as ex:
            self.btn_login.configure(text="Войти в систему",
                                     state="normal")
            self.lbl_err.configure(
                text=f"Ошибка подключения к БД:\n{ex}")
            return

        self.btn_login.configure(text="Войти в систему",
                                 state="normal")

        if user:
            try:
                from services.log_service import log
                log(user["id"], "LOGIN",
                    f"Вход: {user['username']}")
            except Exception:
                pass
            self.destroy()
            self.on_success(user)
        else:
            self.lbl_err.configure(
                text="Неверный логин или пароль")
            self.e_pass.delete(0, "end")
            self.e_pass.focus()
