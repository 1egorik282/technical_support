from PyQt5.QtWidgets import *
from PyQt5.QtCore import Qt
from db_connection import get_connection


class CreateRequestWindow(QWidget):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.categories = []
        self.specialists = []

        self.setWindowTitle("Создание заявки")
        self.resize(700, 620)
        self.setStyleSheet("""
            QWidget {
                background-color: #f0f8ff;
            }
            QLineEdit, QTextEdit, QComboBox {
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
                color: white;
            }
            QLabel {
                color: #2c3e50;
                font-weight: bold;
            }
        """)

        self.load_reference_data()
        self.init_ui()

    def load_reference_data(self):
        conn = get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT category_id, category_name
                FROM request_category
                ORDER BY category_id;
            """)
            self.categories = cursor.fetchall()

            cursor.execute("""
                SELECT u.user_id,
                       CONCAT(u.last_name, ' ', u.first_name, ' ', COALESCE(u.middle_name, '')) AS full_name
                FROM app_user u
                JOIN role r ON u.role_id = r.role_id
                WHERE r.role_name = 'Технический специалист'
                ORDER BY u.last_name, u.first_name;
            """)
            self.specialists = cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(30, 30, 30, 30)

        title = QLabel("➕ Создание новой заявки")
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

        user_info = QLabel(
            f"👤 Автор: {self.user['lastname']} {self.user['name']}\n"
            f"📧 Email: {self.user['email']}"
        )
        user_info.setStyleSheet("""
            color: #34495e;
            padding: 10px;
            background-color: white;
            border-radius: 6px;
        """)
        layout.addWidget(user_info)

        layout.addWidget(QLabel("📂 Категория заявки*:"))
        self.category_combo = QComboBox()
        for category_id, category_name in self.categories:
            self.category_combo.addItem(category_name, category_id)
        layout.addWidget(self.category_combo)

        layout.addWidget(QLabel("📌 Тема заявки*:"))
        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Кратко опишите проблему")
        layout.addWidget(self.subject_input)

        layout.addWidget(QLabel("📝 Описание*:"))
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Подробно опишите проблему...")
        self.description_input.setMaximumHeight(180)
        layout.addWidget(self.description_input)

        layout.addWidget(QLabel("🧑‍💻 Назначить специалиста:"))
        self.assignee_combo = QComboBox()
        self.assignee_combo.addItem("Не назначен", None)
        for specialist_id, specialist_name in self.specialists:
            self.assignee_combo.addItem(specialist_name, specialist_id)
        layout.addWidget(self.assignee_combo)

        if self.user["role"] not in ["Администратор", "Менеджер", "Технический специалист"]:
            self.assignee_combo.setEnabled(False)

        btn_layout = QHBoxLayout()

        self.btn_create = QPushButton("✅ Создать заявку")
        self.btn_create.setStyleSheet("""
            QPushButton { background-color: #27ae60; }
            QPushButton:hover { background-color: #229954; }
        """)
        self.btn_create.clicked.connect(self.create_request)
        btn_layout.addWidget(self.btn_create)

        self.btn_cancel = QPushButton("✖ Отмена")
        self.btn_cancel.setStyleSheet("""
            QPushButton { background-color: #95a5a6; }
            QPushButton:hover { background-color: #7f8c8d; }
        """)
        self.btn_cancel.clicked.connect(self.close)
        btn_layout.addWidget(self.btn_cancel)

        layout.addLayout(btn_layout)
        self.setLayout(layout)

    def create_request(self):
        category_id = self.category_combo.currentData()
        subject = self.subject_input.text().strip()
        description = self.description_input.toPlainText().strip()

        assignee_user_id = self.assignee_combo.currentData()
        if self.user["role"] not in ["Администратор", "Менеджер", "Технический специалист"]:
            assignee_user_id = None

        if not category_id or not subject or not description:
            QMessageBox.warning(self, "Ошибка", "Заполните категорию, тему и описание!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO request (user_id, category_id, assignee_user_id, subject, description)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING request_id;
            """, (self.user["id"], category_id, assignee_user_id, subject, description))
            request_id = cursor.fetchone()[0]

            initial_status = 3 if assignee_user_id else 1
            initial_comment = "Заявка создана и назначена специалисту" if assignee_user_id else "Заявка создана"

            cursor.execute("""
                INSERT INTO request_status_history (request_id, status_id, comment)
                VALUES (%s, %s, %s);
            """, (request_id, initial_status, initial_comment))

            conn.commit()
            QMessageBox.information(self, "Успех", f"Заявка №{request_id} успешно создана!")
            self.close()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка создания заявки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()