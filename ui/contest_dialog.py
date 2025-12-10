from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QLabel, QHBoxLayout
from db import get_all_contests, add_contest, Session
from models import Contest

class ContestDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Управление контестами')
        self.resize(400,300)

        self.listw = QListWidget()
        self.input_name = QLineEdit(); self.input_name.setPlaceholderText('Название контеста')
        self.input_year = QLineEdit(); self.input_year.setPlaceholderText('Год')
        btn_add = QPushButton('Добавить')
        btn_delete = QPushButton('Удалить выбранный')

        btn_add.clicked.connect(self.add_contest)
        btn_delete.clicked.connect(self.delete_contest)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Список контестов:'))
        layout.addWidget(self.listw)
        hl = QHBoxLayout(); hl.addWidget(self.input_name); hl.addWidget(self.input_year); hl.addWidget(btn_add)
        layout.addLayout(hl)
        layout.addWidget(btn_delete)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.listw.clear()
        for c in get_all_contests():
            self.listw.addItem(f"{c.name} | {c.year}")

    def add_contest(self):
        name = self.input_name.text().strip()
        year = self.input_year.text().strip()
        if not name:
            return
        try:
            y = int(year) if year else None
            add_contest(name,y)
            self.input_name.clear(); self.input_year.clear()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))

    def delete_contest(self):
        item = self.listw.currentItem()
        if not item:
            return
        text = item.text()
        parts = text.split('|')
        name = parts[0].strip()
        year = int(parts[1].strip()) if len(parts)>1 else None
        s = Session()
        try:
            c = s.query(Contest).filter_by(name=name, year=year).first()
            if c:
                s.delete(c); s.commit()
            self.refresh()
        finally:
            s.close()
