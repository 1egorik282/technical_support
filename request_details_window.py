from PyQt5.QtWidgets import *
from db_connection import get_connection


class RequestDetailsWindow(QWidget):
    STATUS_TRANSITIONS = {
        1: [2, 3, 6],  # Новая
        2: [3, 4, 6],  # В обработке
        3: [2, 4, 6],  # Назначена специалисту
        4: [5],        # Выполнена
        5: [],         # Закрыта
        6: []          # Отклонена
    }

    def __init__(self, request_id, user):
        super().__init__()
        self.request_id = request_id
        self.user = user
        self.request_data = None
        self.history = []
        self.current_status_id = None
        self.current_status_name = None
        self.specialists = []

        self.setWindowTitle(f"Заявка №{request_id}")
        self.resize(900, 720)
        self.setStyleSheet("""
            QWidget { background-color: #f0f8ff; }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #b0c4de;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #2c3e50;
            }
            QTextEdit, QComboBox {
                background-color: white;
                border: 1px solid #b0c4de;
                border-radius: 5px;
                padding: 8px;
            }
            QPushButton {
                padding: 10px;
                border: none;
                border-radius: 5px;
                font-weight: bold;
                color: white;
            }
            QLabel { color: #2c3e50; }
        """)

        self.main_layout = QVBoxLayout()
        self.main_layout.setSpacing(15)
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(self.main_layout)

        self.refresh_window()

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            child_layout = item.layout()
            if widget is not None:
                widget.deleteLater()
            elif child_layout is not None:
                self.clear_layout(child_layout)

    def load_specialists(self):
        self.specialists = []
        conn = get_connection()
        if not conn:
            return

        cursor = conn.cursor()
        try:
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

    def load_data(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT r.request_id,
                       r.subject,
                       r.description,
                       r.created_at,
                       r.completed_at,
                       c.category_name,
                       CONCAT(author.last_name, ' ', author.first_name, ' ', COALESCE(author.middle_name, '')) AS author_name,
                       author.email,
                       author.phone,
                       r.assignee_user_id,
                       COALESCE(CONCAT(exec.last_name, ' ', exec.first_name, ' ', COALESCE(exec.middle_name, '')), 'Не назначен') AS assignee_name
                FROM request r
                JOIN app_user author ON r.user_id = author.user_id
                LEFT JOIN app_user exec ON r.assignee_user_id = exec.user_id
                LEFT JOIN request_category c ON r.category_id = c.category_id
                WHERE r.request_id = %s;
            """, (self.request_id,))
            self.request_data = cursor.fetchone()

            cursor.execute("""
                SELECT h.status_id, s.status_name, h.changed_at, h.comment
                FROM request_status_history h
                JOIN service_request_status s ON h.status_id = s.status_id
                WHERE h.request_id = %s
                ORDER BY h.changed_at DESC, h.history_id DESC;
            """, (self.request_id,))
            self.history = cursor.fetchall()

            if self.history:
                self.current_status_id = self.history[0][0]
                self.current_status_name = self.history[0][1]
            else:
                self.current_status_id = None
                self.current_status_name = "Не указан"

        except Exception as e:
            self.request_data = None
            self.history = []
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

        self.load_specialists()

    def refresh_window(self):
        self.load_data()
        self.clear_layout(self.main_layout)
        self.build_ui()

    def build_ui(self):
        if not self.request_data:
            self.main_layout.addWidget(QLabel("Заявка не найдена"))
            return

        main_group = QGroupBox("Основная информация")
        main_layout = QFormLayout()

        main_layout.addRow("ID:", QLabel(str(self.request_data[0])))
        main_layout.addRow("Тема:", QLabel(self.request_data[1] or ""))

        desc = QTextEdit()
        desc.setPlainText(self.request_data[2] or "")
        desc.setReadOnly(True)
        desc.setMaximumHeight(120)
        main_layout.addRow("Описание:", desc)

        created = self.request_data[3].strftime("%d.%m.%Y %H:%M") if self.request_data[3] else "Не указано"
        completed = self.request_data[4].strftime("%d.%m.%Y %H:%M") if self.request_data[4] else "Не завершена"

        main_layout.addRow("Дата создания:", QLabel(created))
        main_layout.addRow("Дата завершения:", QLabel(completed))
        main_layout.addRow("Категория:", QLabel(self.request_data[5] or "Не указана"))
        main_layout.addRow("Автор:", QLabel(self.request_data[6] or ""))
        main_layout.addRow("Email:", QLabel(self.request_data[7] or ""))
        main_layout.addRow("Телефон:", QLabel(self.request_data[8] or "Не указан"))
        main_layout.addRow("Исполнитель:", QLabel(self.request_data[10] or "Не назначен"))
        main_layout.addRow("Текущий статус:", QLabel(self.current_status_name or "Не указан"))

        main_group.setLayout(main_layout)
        self.main_layout.addWidget(main_group)

        history_group = QGroupBox("История статусов")
        history_layout = QVBoxLayout()

        history_text = QTextEdit()
        history_text.setReadOnly(True)
        history_text.setMaximumHeight(220)

        history_content = ""
        for _, status_name, changed_at, comment in self.history:
            date_str = changed_at.strftime("%d.%m.%Y %H:%M") if changed_at else "Не указано"
            history_content += f"📌 {status_name} — {date_str}\n"
            if comment:
                history_content += f"   💬 {comment}\n"
            history_content += "\n"

        history_text.setPlainText(history_content.strip())
        history_layout.addWidget(history_text)
        history_group.setLayout(history_layout)
        self.main_layout.addWidget(history_group)

        if self.user["role"] in ["Администратор", "Менеджер", "Технический специалист"]:
            control_group = QGroupBox("Управление заявкой")
            control_layout = QVBoxLayout()

            # Назначение специалиста
            assign_layout = QHBoxLayout()
            assign_layout.addWidget(QLabel("Назначить специалиста:"))

            self.assignee_combo = QComboBox()
            self.assignee_combo.addItem("Не назначен", None)
            current_assignee_id = self.request_data[9]

            for specialist_id, specialist_name in self.specialists:
                self.assignee_combo.addItem(specialist_name, specialist_id)

            for i in range(self.assignee_combo.count()):
                if self.assignee_combo.itemData(i) == current_assignee_id:
                    self.assignee_combo.setCurrentIndex(i)
                    break

            assign_layout.addWidget(self.assignee_combo)

            btn_assign = QPushButton("🧑‍💻 Назначить")
            btn_assign.setStyleSheet("background-color: #8e44ad;")
            btn_assign.clicked.connect(self.assign_specialist)
            assign_layout.addWidget(btn_assign)

            control_layout.addLayout(assign_layout)

            # Изменение статуса
            status_layout = QHBoxLayout()
            status_layout.addWidget(QLabel("Изменить статус:"))

            self.status_combo = QComboBox()
            available_statuses = self.get_available_statuses()
            for status_id, status_name in available_statuses:
                self.status_combo.addItem(status_name, status_id)
            status_layout.addWidget(self.status_combo)

            btn_change_status = QPushButton("🔄 Сохранить статус")
            btn_change_status.setStyleSheet("background-color: #3498db;")
            btn_change_status.clicked.connect(self.change_status)
            status_layout.addWidget(btn_change_status)

            control_layout.addLayout(status_layout)

            control_layout.addWidget(QLabel("Комментарий к изменению:"))
            self.comment_input = QTextEdit()
            self.comment_input.setMaximumHeight(90)
            control_layout.addWidget(self.comment_input)

            control_group.setLayout(control_layout)
            self.main_layout.addWidget(control_group)

        btn_close = QPushButton("✖ Закрыть")
        btn_close.setStyleSheet("background-color: #95a5a6;")
        btn_close.clicked.connect(self.close)
        self.main_layout.addWidget(btn_close)

    def get_available_statuses(self):
        if self.current_status_id is None:
            return []

        allowed_ids = self.STATUS_TRANSITIONS.get(self.current_status_id, [])
        if not allowed_ids:
            return []

        conn = get_connection()
        if not conn:
            return []

        cursor = conn.cursor()
        try:
            cursor.execute("""
                SELECT status_id, status_name
                FROM service_request_status
                WHERE status_id = ANY(%s)
                ORDER BY status_id;
            """, (allowed_ids,))
            return cursor.fetchall()
        finally:
            cursor.close()
            conn.close()

    def assign_specialist(self):
        assignee_user_id = self.assignee_combo.currentData()

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                UPDATE request
                SET assignee_user_id = %s
                WHERE request_id = %s;
            """, (assignee_user_id, self.request_id))

            if assignee_user_id:
                cursor.execute("""
                    INSERT INTO request_status_history (request_id, status_id, comment)
                    VALUES (%s, 3, 'Назначен специалист');
                """, (self.request_id,))

            conn.commit()
            QMessageBox.information(self, "Успех", "Исполнитель обновлен!")
            self.refresh_window()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка назначения:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def change_status(self):
        status_id = self.status_combo.currentData()
        comment = self.comment_input.toPlainText().strip() or None

        if status_id is None:
            QMessageBox.warning(self, "Ошибка", "Нет доступных переходов для статуса!")
            return

        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO request_status_history (request_id, status_id, comment)
                VALUES (%s, %s, %s);
            """, (self.request_id, status_id, comment))

            if status_id in (4, 5):
                cursor.execute("""
                    UPDATE request
                    SET completed_at = CURRENT_TIMESTAMP
                    WHERE request_id = %s AND completed_at IS NULL;
                """, (self.request_id,))
            elif status_id in (1, 2, 3):
                cursor.execute("""
                    UPDATE request
                    SET completed_at = NULL
                    WHERE request_id = %s;
                """, (self.request_id,))

            conn.commit()
            QMessageBox.information(self, "Успех", "Статус изменен!")
            self.refresh_window()

        except Exception as e:
            conn.rollback()
            QMessageBox.critical(self, "Ошибка", f"Ошибка изменения статуса:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()