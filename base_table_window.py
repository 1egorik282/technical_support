from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QHeaderView, QPushButton, QTableWidgetItem
)
from PyQt5.QtCore import Qt


class TableWindow(QWidget):
    def __init__(self, table_name, columns, window_title, user=None):
        super().__init__()
        self.table_name = table_name
        self.columns = columns
        self.user = user

        self.setWindowTitle(window_title)
        self.resize(1100, 650)
        self.setStyleSheet("""
            QWidget {
                background-color: #f5f7fa;
            }
            QTableWidget {
                background-color: white;
                alternate-background-color: #f8f9fa;
                gridline-color: #dee2e6;
                border: 1px solid #dcdde1;
                border-radius: 6px;
            }
            QHeaderView::section {
                background-color: #2c3e50;
                color: white;
                padding: 10px;
                font-weight: bold;
                border: none;
            }
            QPushButton {
                padding: 9px 16px;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                color: white;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #dcdde1;
                border-radius: 6px;
                background-color: white;
            }
            QLabel {
                font-weight: bold;
                color: #2c3e50;
            }
        """)

        self.init_ui()
        self.load_data()

    def init_ui(self):
        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Поиск:"))

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Введите текст для поиска...")
        self.search_input.textChanged.connect(self.search_data)
        search_layout.addWidget(self.search_input)

        layout.addLayout(search_layout)

        self.table = QTableWidget()
        self.table.setColumnCount(len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.doubleClicked.connect(self.on_double_click)
        layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()

        self.btn_refresh = QPushButton("🔄 Обновить")
        self.btn_refresh.setStyleSheet("background-color: #3498db;")
        self.btn_refresh.clicked.connect(self.load_data)
        buttons_layout.addWidget(self.btn_refresh)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        self.setLayout(layout)

    def load_data(self):
        pass

    def search_data(self):
        search_text = self.search_input.text().lower().strip()

        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def on_double_click(self, index):
        pass