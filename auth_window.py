import sys
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton,
    QMessageBox, QHBoxLayout, QDialog, QApplication
)
from PyQt5.QtCore import Qt
from db_connection import get_connection
from main_menu import MainMenu
from register_window import RegisterWindow


class AuthWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Авторизация - Система управления заявками")
        self.resize(460, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLineEdit {
                padding: 10px;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                padding: 12px;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(40, 30, 40, 30)

        title = QLabel("📋 Система управления заявками")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: #2c3e50;
            padding: 20px;
            background-color: #e6f3ff;
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)
        layout.addWidget(title)

        layout.addSpacing(20)

        layout.addWidget(QLabel("📧 Email:"))
        self.input_email = QLineEdit()
        self.input_email.setPlaceholderText("Введите email")
        layout.addWidget(self.input_email)

        layout.addWidget(QLabel("🔒 Пароль:"))
        self.input_password = QLineEdit()
        self.input_password.setPlaceholderText("Введите пароль")
        self.input_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.input_password)

        layout.addSpacing(10)

        buttons_layout = QHBoxLayout()

        self.btn_login = QPushButton("🚪 Войти")
        self.btn_login.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        self.btn_login.clicked.connect(self.check_login)
        buttons_layout.addWidget(self.btn_login)

        self.btn_register = QPushButton("📝 Регистрация")
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_register.clicked.connect(self.show_register)
        buttons_layout.addWidget(self.btn_register)

        layout.addLayout(buttons_layout)

        self.btn_forgot = QPushButton("❓ Забыли пароль?")
        self.btn_forgot.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #3498db;
                border: none;
                font-size: 12px;
                text-decoration: underline;
                padding: 5px;
            }
            QPushButton:hover {
                color: #2980b9;
            }
        """)
        self.btn_forgot.clicked.connect(self.show_password_recovery)
        layout.addWidget(self.btn_forgot)

        self.setLayout(layout)

    def check_login(self):
        email = self.input_email.text().strip().lower()
        password = self.input_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Ошибка", "Введите email и пароль!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT 
                    u.user_id,
                    u.email,
                    u.password,
                    u.last_name,
                    u.first_name,
                    u.middle_name,
                    COALESCE(r.role_name, 'Пользователь') AS role_name,
                    u.position_id,
                    COALESCE(p.position_name, 'Не указана') AS position_name,
                    u.phone
                FROM app_user u
                LEFT JOIN role r ON u.role_id = r.role_id
                LEFT JOIN position p ON u.position_id = p.position_id
                WHERE u.email = %s;
            """, (email,))

            user = cursor.fetchone()

            if not user:
                QMessageBox.warning(self, "Ошибка", "Пользователь не найден!")
                return

            if password != (user[2] or ""):
                QMessageBox.warning(self, "Ошибка", "Неверный пароль!")
                return

            user_data = {
                "id": user[0],
                "email": user[1],
                "lastname": user[3] or "",
                "name": user[4] or "",
                "middlename": user[5] or "",
                "role": user[6] or "Пользователь",
                "position_id": user[7],
                "position_name": user[8] or "Не указана",
                "telephone": user[9] or ""
            }

            full_name = f"{user_data['lastname']} {user_data['name']}".strip()
            if user_data["middlename"]:
                full_name += f" {user_data['middlename']}"

            QMessageBox.information(
                self,
                "Успех",
                f"Добро пожаловать, {full_name}!\n"
                f"Роль: {user_data['role']}\n"
                f"Должность: {user_data['position_name']}"
            )

            self.open_main_menu(user_data)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка при входе:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def show_register(self):
        self.register_window = RegisterWindow()
        self.register_window.show()

    def show_password_recovery(self):
        dialog = QDialog(self)
        dialog.setWindowTitle("Восстановление пароля")
        dialog.resize(420, 270)

        layout = QVBoxLayout(dialog)

        title = QLabel("🔐 Восстановление пароля")
        title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; padding: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        layout.addWidget(QLabel("Введите ваш email:"))
        input_email = QLineEdit()
        input_email.setPlaceholderText("Email")
        layout.addWidget(input_email)

        layout.addWidget(QLabel("Введите вашу фамилию:"))
        input_surname = QLineEdit()
        input_surname.setPlaceholderText("Фамилия")
        layout.addWidget(input_surname)

        btn_layout = QHBoxLayout()

        btn_recover = QPushButton("✅ Восстановить")
        btn_recover.setStyleSheet("background-color: #27ae60; color: white; padding: 10px;")
        btn_recover.clicked.connect(
            lambda: self.recover_password(dialog, input_email.text(), input_surname.text())
        )
        btn_layout.addWidget(btn_recover)

        btn_cancel = QPushButton("✖ Отмена")
        btn_cancel.setStyleSheet("background-color: #95a5a6; color: white; padding: 10px;")
        btn_cancel.clicked.connect(dialog.reject)
        btn_layout.addWidget(btn_cancel)

        layout.addLayout(btn_layout)
        dialog.exec_()

    def recover_password(self, dialog, email, surname):
        email = email.strip().lower()
        surname = surname.strip()

        if not email or not surname:
            QMessageBox.warning(dialog, "Ошибка", "Заполните все поля!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(dialog, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT password, last_name
                FROM app_user
                WHERE email = %s;
            """, (email,))
            user = cursor.fetchone()

            if not user:
                QMessageBox.warning(dialog, "Ошибка", "Пользователь не найден!")
                return

            if (user[1] or "").strip().lower() != surname.lower():
                QMessageBox.warning(dialog, "Ошибка", "Фамилия не совпадает!")
                return

            QMessageBox.information(
                dialog,
                "Ваш пароль",
                f"Email: {email}\nПароль: {user[0]}\n\nРекомендуем сменить пароль после входа!"
            )
            dialog.accept()

        except Exception as e:
            QMessageBox.critical(dialog, "Ошибка", f"Ошибка:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def open_main_menu(self, user_data):
        self.main_menu = MainMenu(user_data)
        self.main_menu.show()
        self.hide()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = AuthWindow()
    window.show()
    sys.exit(app.exec_())