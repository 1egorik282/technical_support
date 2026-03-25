from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db_connection import get_connection


class ChangePasswordWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.setWindowTitle("Смена пароля")
        self.resize(450, 400)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLineEdit {
                padding: 12px;
                border: 2px solid #bdc3c7;
                border-radius: 8px;
                font-size: 14px;
                background-color: white;
            }
            QPushButton {
                padding: 12px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("🔐 Смена пароля")
        title.setStyleSheet("""
            font-size: 20px;
            font-weight: bold;
            color: white;
            padding: 20px;
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #3498db, stop:1 #2980b9);
            border-radius: 10px;
        """)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        info_label = QLabel(f"👤 Пользователь: {self.user['lastname']} {self.user['name']}")
        info_label.setStyleSheet("""
            color: #34495e;
            font-size: 14px;
            padding: 10px;
            background-color: white;
            border-radius: 5px;
        """)
        info_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(info_label)

        layout.addWidget(QLabel("🔑 Текущий пароль:"))
        self.old_password = QLineEdit()
        self.old_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.old_password)

        layout.addWidget(QLabel("🆕 Новый пароль:"))
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.new_password)

        layout.addWidget(QLabel("✅ Подтверждение:"))
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.confirm_password)

        btn_layout = QHBoxLayout()

        self.btn_save = QPushButton("✅ Сохранить")
        self.btn_save.setStyleSheet("background-color: #27ae60;")
        self.btn_save.clicked.connect(self.change_password)
        btn_layout.addWidget(self.btn_save)

        self.btn_cancel = QPushButton("✖ Отмена")
        self.btn_cancel.setStyleSheet("background-color: #95a5a6;")
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def change_password(self):
        old_pass = self.old_password.text().strip()
        new_pass = self.new_password.text().strip()
        confirm = self.confirm_password.text().strip()

        if not old_pass or not new_pass or not confirm:
            QMessageBox.warning(self, "Ошибка", "Заполните все поля!")
            return

        if new_pass != confirm:
            QMessageBox.warning(self, "Ошибка", "Новые пароли не совпадают!")
            return

        if len(new_pass) < 4:
            QMessageBox.warning(self, "Ошибка", "Пароль должен быть минимум 4 символа!")
            return

        if old_pass == new_pass:
            QMessageBox.warning(self, "Ошибка", "Новый пароль не должен совпадать с текущим!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к базе данных")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT password FROM app_user WHERE user_id = %s;", (self.user["id"],))
            row = cursor.fetchone()

            if not row:
                QMessageBox.critical(self, "Ошибка", "Пользователь не найден")
                return

            if old_pass != (row[0] or ""):
                QMessageBox.warning(self, "Ошибка", "Неверный текущий пароль!")
                return

            cursor.execute(
                "UPDATE app_user SET password = %s WHERE user_id = %s;",
                (new_pass, self.user["id"])
            )
            conn.commit()

            QMessageBox.information(self, "Успех", "✅ Пароль успешно изменен!")
            self.close()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка при смене пароля:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()