import customtkinter as ctk

ctk.set_appearance_mode("light")
ctk.set_default_color_theme("green")


def main():
    root = ctk.CTk()
    root.geometry("1366x768")
    root.minsize(1100, 650)
    root.title("Система учёта ресурсов — ООО ТК «Новочебоксарский»")
    root.withdraw()

    def on_login(user: dict):
        root.deiconify()
        from ui.main_window import MainWindow
        MainWindow(root, user, on_logout=restart)

    def restart():
        for w in root.winfo_children():
            w.destroy()
        root.withdraw()
        open_login()

    def open_login():
        from ui.login_window import LoginWindow
        LoginWindow(root, on_success=on_login)

    open_login()
    root.mainloop()


if __name__ == "__main__":
    main()
