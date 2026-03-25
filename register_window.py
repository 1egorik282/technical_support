import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QMessageBox, QComboBox,
    QHBoxLayout, QGroupBox
)
from PyQt5.QtCore import Qt
from db_connection import get_connection


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Регистрация сотрудника")
        self.resize(500, 680)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLineEdit, QComboBox {
                padding: 10px;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                font-size: 14px;
                background-color: white;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 10px;
                color: #2c3e50;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
            QPushButton {
                border-radius: 6px;
            }
        """)

        self.roles = []
        self.positions = []

        self.load_reference_data()
        self.init_ui()

    def load_reference_data(self):
        conn = get_connection()
        if not conn:
            self.roles = [(3, "Пользователь")]
            self.positions = [(4, "Специалист")]
            return

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT role_id, role_name FROM role ORDER BY role_id;")
            self.roles = cursor.fetchall()

            cursor.execute("SELECT position_id, position_name FROM position ORDER BY position_id;")
            self.positions = cursor.fetchall()

            if not self.roles:
                self.roles = [(3, "Пользователь")]
            if not self.positions:
                self.positions = [(4, "Специалист")]

        except Exception:
            self.roles = [(3, "Пользователь")]
            self.positions = [(4, "Специалист")]
        finally:
            cursor.close()
            conn.close()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(30, 20, 30, 20)

        title = QLabel("📝 Регистрация нового сотрудника")
        title.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #2c3e50;
            padding: 15px;
            background-color: #e6f3ff;
            border-radius: 8px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        fio_group = QGroupBox("ФИО сотрудника")
        fio_layout = QVBoxLayout()

        fio_layout.addWidget(QLabel("Фамилия*:"))
        self.input_surname = QLineEdit()
        fio_layout.addWidget(self.input_surname)

        fio_layout.addWidget(QLabel("Имя*:"))
        self.input_name = QLineEdit()
        fio_layout.addWidget(self.input_name)

        fio_layout.addWidget(QLabel("Отчество:"))
        self.input_middlename = QLineEdit()
        fio_layout.addWidget(self.input_middlename)

        fio_group.setLayout(fio_layout)
        layout.addWidget(fio_group)

        auth_group = QGroupBox("Учетные данные")
        auth_layout = QVBoxLayout()

        auth_layout.addWidget(QLabel("Email*:"))
        self.input_email = QLineEdit()
        auth_layout.addWidget(self.input_email)

        auth_layout.addWidget(QLabel("Телефон:"))
        self.input_phone = QLineEdit()
        auth_layout.addWidget(self.input_phone)

        auth_layout.addWidget(QLabel("Пароль*:"))
        self.input_password = QLineEdit()
        self.input_password.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.input_password)

        auth_layout.addWidget(QLabel("Подтверждение*:"))
        self.input_confirm = QLineEdit()
        self.input_confirm.setEchoMode(QLineEdit.Password)
        auth_layout.addWidget(self.input_confirm)

        auth_group.setLayout(auth_layout)
        layout.addWidget(auth_group)

        role_group = QGroupBox("Роль и должность")
        role_layout = QVBoxLayout()

        role_layout.addWidget(QLabel("Роль*:"))
        self.combo_role = QComboBox()
        for role_id, role_name in self.roles:
            self.combo_role.addItem(str(role_name), role_id)
        role_layout.addWidget(self.combo_role)

        role_layout.addWidget(QLabel("Должность*:"))
        self.combo_position = QComboBox()
        for pos_id, pos_name in self.positions:
            self.combo_position.addItem(str(pos_name), pos_id)
        role_layout.addWidget(self.combo_position)

        role_group.setLayout(role_layout)
        layout.addWidget(role_group)

        info = QLabel("* - обязательные поля")
        info.setStyleSheet("color: #e74c3c; font-size: 11px;")
        layout.addWidget(info)

        btn_layout = QHBoxLayout()

        self.btn_register = QPushButton("✅ Зарегистрироваться")
        self.btn_register.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71;
                color: white;
                padding: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        self.btn_register.clicked.connect(self.register_user)
        btn_layout.addWidget(self.btn_register)

        self.btn_cancel = QPushButton("✖ Отмена")
        self.btn_cancel.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                padding: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def register_user(self):
        lastname = self.input_surname.text().strip()
        firstname = self.input_name.text().strip()
        middlename = self.input_middlename.text().strip() or None
        email = self.input_email.text().strip().lower()
        phone = self.input_phone.text().strip() or None
        password = self.input_password.text().strip()
        confirm = self.input_confirm.text().strip()
        role_id = self.combo_role.currentData()
        position_id = self.combo_position.currentData()

        if not all([lastname, firstname, email, password, confirm]):
            QMessageBox.warning(self, "Ошибка", "Заполните все обязательные поля!")
            return

        if password != confirm:
            QMessageBox.warning(self, "Ошибка", "Пароли не совпадают!")
            return

        if "@" not in email or "." not in email:
            QMessageBox.warning(self, "Ошибка", "Введите корректный email!")
            return

        if len(password) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть минимум 4 символа!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT 1 FROM app_user WHERE email = %s;", (email,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Ошибка", "Пользователь с таким email уже существует!")
                return

            cursor.execute("""
                INSERT INTO app_user (
                    role_id, position_id, first_name, last_name, middle_name, email, phone, password
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s);
            """, (role_id, position_id, firstname, lastname, middlename, email, phone, password))

            conn.commit()

            QMessageBox.information(
                self,
                "Успех",
                f"✅ Сотрудник зарегистрирован!\n\n"
                f"ФИО: {lastname} {firstname} {middlename or ''}\n"
                f"Email: {email}\n"
                f"Телефон: {phone or 'Не указан'}\n"
                f"Роль: {self.combo_role.currentText()}\n"
                f"Должность: {self.combo_position.currentText()}"
            )
            self.close()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка регистрации:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RegisterWindow()
    window.show()
    sys.exit(app.exec_())