from PyQt5.QtWidgets import QMessageBox, QTableWidgetItem
from PyQt5.QtGui import QColor, QBrush
from db_connection import get_connection
from base_table_window import TableWindow


class RequestsWindow(TableWindow):
    def __init__(self, user, show_all=False):
        self.user = user
        self.show_all = show_all
        columns = [
            "ID", "Категория", "Тема", "Статус",
            "Дата создания", "Дата завершения",
            "Автор", "Исполнитель"
        ]
        super().__init__("request", columns, "📋 Заявки", user)

    def load_data(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Ошибка", "Не удалось подключиться к БД")
            return

        cursor = conn.cursor()
        try:
            base_query = """
                SELECT r.request_id,
                       COALESCE(c.category_name, 'Не указана') AS category_name,
                       r.subject,
                       s.status_name,
                       r.created_at,
                       r.completed_at,
                       CONCAT(author.last_name, ' ', author.first_name, ' ', COALESCE(author.middle_name, '')) AS author_name,
                       COALESCE(CONCAT(exec.last_name, ' ', exec.first_name, ' ', COALESCE(exec.middle_name, '')), 'Не назначен') AS assignee_name
                FROM request r
                JOIN app_user author ON r.user_id = author.user_id
                LEFT JOIN app_user exec ON r.assignee_user_id = exec.user_id
                LEFT JOIN request_category c ON r.category_id = c.category_id
                JOIN request_status_history h ON r.request_id = h.request_id
                JOIN service_request_status s ON h.status_id = s.status_id
                WHERE h.changed_at = (
                    SELECT MAX(h2.changed_at)
                    FROM request_status_history h2
                    WHERE h2.request_id = r.request_id
                )
            """

            if self.show_all:
                if self.user["role"] == "Технический специалист":
                    cursor.execute(base_query + """
                        AND (r.assignee_user_id = %s OR r.assignee_user_id IS NULL)
                        ORDER BY r.created_at DESC, r.request_id DESC;
                    """, (self.user["id"],))
                else:
                    cursor.execute(base_query + """
                        ORDER BY r.created_at DESC, r.request_id DESC;
                    """)
            else:
                cursor.execute(base_query + """
                    AND r.user_id = %s
                    ORDER BY r.created_at DESC, r.request_id DESC;
                """, (self.user["id"],))

            data = cursor.fetchall()
            self.table.setRowCount(len(data))

            for row_idx, row in enumerate(data):
                for col_idx, value in enumerate(row):
                    if value is None:
                        text = ""
                    elif col_idx in (4, 5) and hasattr(value, "strftime"):
                        text = value.strftime("%d.%m.%Y %H:%M")
                    else:
                        text = str(value)

                    item = QTableWidgetItem(text)

                    if col_idx == 3:
                        lower_status = text.lower()
                        if "выполн" in lower_status or "закрыт" in lower_status:
                            item.setForeground(QBrush(QColor("#27ae60")))
                        elif "отклон" in lower_status:
                            item.setForeground(QBrush(QColor("#e74c3c")))
                        elif "обработ" in lower_status or "назнач" in lower_status:
                            item.setForeground(QBrush(QColor("#f39c12")))
                        elif "новая" in lower_status:
                            item.setForeground(QBrush(QColor("#3498db")))

                    self.table.setItem(row_idx, col_idx, item)

        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Ошибка загрузки:\n{str(e)}")
        finally:
            cursor.close()
            conn.close()

    def on_double_click(self, index):
        row = self.table.currentRow()
        if row >= 0:
            request_id = self.table.item(row, 0).text()
            self.open_request_details(request_id)

    def open_request_details(self, request_id):
        from request_details_window import RequestDetailsWindow
        self.details_window = RequestDetailsWindow(int(request_id), self.user)
        self.details_window.show()