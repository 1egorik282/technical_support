import sys
from PyQt5.QtWidgets import QApplication, QMessageBox
from auth_window import AuthWindow
from db_connection import init_database


if __name__ == "__main__":
    app = QApplication(sys.argv)

    if not init_database():
        QMessageBox.critical(
            None,
            "Ошибка подключения",
            "Не удалось подключиться к PostgreSQL.\nПроверьте настройки в db_connection.py"
        )
        sys.exit(1)

    window = AuthWindow()
    window.show()

    sys.exit(app.exec_())