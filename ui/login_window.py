from PyQt5.QtWidgets import QDialog, QLineEdit, QPushButton, QVBoxLayout, QLabel, QMessageBox
import config

class LoginWindow(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Вход администратора")
        self.resize(300,120)

        self.user_is_admin = False 

        self.login_input = QLineEdit()
        self.login_input.setPlaceholderText("Логин")

        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Пароль")
        self.pass_input.setEchoMode(QLineEdit.Password)

        self.btn_login = QPushButton("Войти")
        self.btn_guest = QPushButton("Продолжить как гость")

        layout = QVBoxLayout()
        layout.addWidget(QLabel("Авторизация администратора"))
        layout.addWidget(self.login_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.btn_login)
        layout.addWidget(self.btn_guest)

        self.setLayout(layout)

        self.btn_login.clicked.connect(self.try_login)
        self.btn_guest.clicked.connect(self.continue_as_guest)

    def try_login(self):
        if self.login_input.text() == config.ADMIN_USERNAME and self.pass_input.text() == config.ADMIN_PASSWORD:
            self.user_is_admin = True
            self.accept()
        else:
            QMessageBox.warning(self, "Ошибка", "Неверный логин или пароль")

    def continue_as_guest(self):
        self.user_is_admin = False
        self.accept()
