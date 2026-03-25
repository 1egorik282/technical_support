from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db_connection import get_connection
from requests_window import RequestsWindow
from change_password_window import ChangePasswordWindow
from create_request_window import CreateRequestWindow


class MainMenu(QWidget):
    def __init__(self, user_data):
        super().__init__()
        self.user = user_data
        self.setWindowTitle(f"Главное меню - {self.user['lastname']} {self.user['name']}")
        self.resize(550, 620)
        self.setStyleSheet("""
            QWidget { background-color: #f0f8ff; }
            QPushButton {
                padding: 15px;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: white;
            }
            QLabel { color: #2c3e50; }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        full_name = f"{self.user['lastname']} {self.user['name']}".strip()
        if self.user.get("middlename"):
            full_name += f" {self.user['middlename']}"

        header = QLabel(
            f"👤 {full_name}\n"
            f"📌 Роль: {self.user['role']}\n"
            f"💼 Должность: {self.user['position_name']}\n"
            f"📧 {self.user['email']}"
        )
        header.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                stop:0 #2c3e50, stop:1 #34495e);
            color: white;
            padding: 20px;
            font-size: 15px;
            border-radius: 10px;
        """)
        header.setAlignment(Qt.AlignCenter)
        layout.addWidget(header)

        stats = self.get_statistics()
        stats_label = QLabel(f"📊 Статистика:\n{stats}")
        stats_label.setStyleSheet("""
            background-color: white;
            padding: 15px;
            border-radius: 8px;
            font-size: 13px;
        """)
        stats_label.setWordWrap(True)
        layout.addWidget(stats_label)

        btn_requests = QPushButton("📋 Мои заявки")
        btn_requests.setStyleSheet("background-color: #3498db;")
        btn_requests.clicked.connect(self.open_my_requests)
        layout.addWidget(btn_requests)

        btn_new = QPushButton("➕ Создать заявку")
        btn_new.setStyleSheet("background-color: #27ae60;")
        btn_new.clicked.connect(self.create_request)
        layout.addWidget(btn_new)

        if self.user["role"] in ["Администратор", "Менеджер", "Технический специалист"]:
            btn_all = QPushButton("📚 Все заявки")
            btn_all.setStyleSheet("background-color: #9b59b6;")
            btn_all.clicked.connect(self.open_all_requests)
            layout.addWidget(btn_all)

        btn_change_password = QPushButton("🔐 Сменить пароль")
        btn_change_password.setStyleSheet("background-color: #f39c12;")
        btn_change_password.clicked.connect(self.open_change_password)
        layout.addWidget(btn_change_password)

        btn_logout = QPushButton("🚪 Выйти")
        btn_logout.setStyleSheet("background-color: #95a5a6;")
        btn_logout.clicked.connect(self.logout)
        layout.addWidget(btn_logout)

        self.setLayout(layout)

    def get_statistics(self):
        conn = get_connection()
        if not conn:
            return "Ошибка подключения"

        cursor = conn.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM request;")
            total = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM request WHERE completed_at IS NULL;")
            active = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM request WHERE user_id = %s;", (self.user["id"],))
            my_total = cursor.fetchone()[0]

            cursor.execute("""
                SELECT COUNT(*)
                FROM request
                WHERE user_id = %s AND completed_at IS NULL;
            """, (self.user["id"],))
            my_active = cursor.fetchone()[0]

            return (
                f"Всего заявок: {total}\n"
                f"Активных: {active}\n"
                f"Моих заявок: {my_total}\n"
                f"Моих активных: {my_active}"
            )

        except Exception as e:
            return f"Ошибка: {e}"
        finally:
            cursor.close()
            conn.close()

    def open_my_requests(self):
        self.requests_window = RequestsWindow(self.user, show_all=False)
        self.requests_window.show()

    def open_all_requests(self):
        self.requests_window = RequestsWindow(self.user, show_all=True)
        self.requests_window.show()

    def create_request(self):
        self.create_window = CreateRequestWindow(self.user)
        self.create_window.show()

    def open_change_password(self):
        self.change_password_window = ChangePasswordWindow(self.user)
        self.change_password_window.show()

    def logout(self):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Подтверждение")
        msg_box.setText("Вы уверены, что хотите выйти?")
        msg_box.setIcon(QMessageBox.Question)

        yes_button = msg_box.addButton("Да", QMessageBox.YesRole)
        no_button = msg_box.addButton("Нет", QMessageBox.NoRole)

        msg_box.setStyleSheet("""
            QMessageBox {
                background-color: #f0f8ff;
            }
            QLabel {
                color: #2c3e50;
                font-size: 13px;
            }
            QPushButton {
                min-width: 90px;
                min-height: 32px;
                border-radius: 6px;
                font-weight: bold;
                padding: 6px 12px;
            }
        """)

        yes_button.setStyleSheet("background-color: #e74c3c; color: white;")
        no_button.setStyleSheet("background-color: #95a5a6; color: white;")

        msg_box.exec_()

        if msg_box.clickedButton() == yes_button:
            from auth_window import AuthWindow
            self.auth_window = AuthWindow()
            self.auth_window.show()
            self.close()