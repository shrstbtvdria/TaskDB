import sys
from PyQt5.QtWidgets import QApplication
from ui.login_window import LoginWindow
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    login = LoginWindow()
    if login.exec():
        is_admin = login.user_is_admin
        window = MainWindow(is_admin=is_admin)
        window.show()
        sys.exit(app.exec())

if __name__ == '__main__':
    main()
