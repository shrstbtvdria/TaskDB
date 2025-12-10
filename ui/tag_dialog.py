from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QPushButton, QListWidget, QMessageBox, QLabel, QHBoxLayout
from db import get_all_tags, add_tag, Session
from models import Tag

class TagDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('Управление тегами')
        self.resize(400,300)

        self.listw = QListWidget()
        self.input = QLineEdit(); self.input.setPlaceholderText('Новый тег')
        btn_add = QPushButton('Добавить')
        btn_delete = QPushButton('Удалить выбранный')

        btn_add.clicked.connect(self.add_tag)
        btn_delete.clicked.connect(self.delete_tag)

        layout = QVBoxLayout()
        layout.addWidget(QLabel('Список тегов:'))
        layout.addWidget(self.listw)
        hl = QHBoxLayout(); hl.addWidget(self.input); hl.addWidget(btn_add)
        layout.addLayout(hl)
        layout.addWidget(btn_delete)
        self.setLayout(layout)
        self.refresh()

    def refresh(self):
        self.listw.clear()
        for t in get_all_tags():
            self.listw.addItem(t.name)

    def add_tag(self):
        name = self.input.text().strip()
        if not name:
            return
        try:
            add_tag(name)
            self.input.clear()
            self.refresh()
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))

    def delete_tag(self):
        item = self.listw.currentItem()
        if not item:
            return
        name = item.text()
        s = Session()
        try:
            tag = s.query(Tag).filter_by(name=name).first()
            if tag:
                s.delete(tag); s.commit()
            self.refresh()
        finally:
            s.close()
