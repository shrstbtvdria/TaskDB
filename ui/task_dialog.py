from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QVBoxLayout, QLineEdit, QTextEdit, QLabel, QSpinBox, QCheckBox, QPushButton, QHBoxLayout, QListWidget, QListWidgetItem, QMessageBox
from db import get_all_contests, Session
from models import Tag, Contest, Task

class TaskDialog(QDialog):
    def __init__(self, parent=None, task=None, read_only=False):
        super().__init__(parent)
        self.setWindowTitle('Добавить/Редактировать задачу')
        self.resize(600,500)
        self.task = task

        self.title = QLineEdit()
        self.title.setPlaceholderText('Название (рус)')

        self.description = QTextEdit()
        self.description.setPlaceholderText('Краткое условие')

        self.solution = QTextEdit()
        self.solution.setPlaceholderText('Краткая идея решения')

        self.polygon = QLineEdit()
        self.polygon.setPlaceholderText('Ссылка на Polygon')

        self.prepared_cf = QCheckBox('Codeforces')
        self.prepared_yandex = QCheckBox('Yandex Contest')

        self.difficulty = QSpinBox()
        self.difficulty.setRange(1,10)
        self.difficulty.setValue(1)

        self.note = QTextEdit()
        self.note.setPlaceholderText('Примечание')

        self.tags_input = QLineEdit()
        self.tags_input.setPlaceholderText('Теги через запятую')

        self.contest_list = QListWidget()
        self.contest_list.setSelectionMode(QListWidget.MultiSelection)

        self.read_only = read_only
        
        for c in get_all_contests():
            item = QListWidgetItem(f"{c.name} ({c.year})")
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            item.setData(Qt.UserRole, c.id)
            self.contest_list.addItem(item)

        # кнопки
        btn_save = QPushButton('Сохранить')
        btn_cancel = QPushButton('Отмена')

        btn_save.clicked.connect(self.save)
        btn_cancel.clicked.connect(self.reject)

        # режим просмотра
        if self.read_only:
            self.title.setReadOnly(True)
            self.description.setReadOnly(True)
            self.solution.setReadOnly(True)
            self.polygon.setReadOnly(True)
            self.prepared_cf.setEnabled(False)
            self.prepared_yandex.setEnabled(False)
            self.difficulty.setEnabled(False)
            self.note.setReadOnly(True)
            self.tags_input.setReadOnly(True)
            self.contest_list.setEnabled(False)
            btn_save.setVisible(False)

        # LAYOUT
        layout = QVBoxLayout()
        layout.addWidget(QLabel('Название:')); layout.addWidget(self.title)
        layout.addWidget(QLabel('Условие:')); layout.addWidget(self.description)
        layout.addWidget(QLabel('Идея решения:')); layout.addWidget(self.solution)
        layout.addWidget(QLabel('Ссылка на Polygon:')); layout.addWidget(self.polygon)
        layout.addWidget(self.prepared_cf); layout.addWidget(self.prepared_yandex)
        layout.addWidget(QLabel('Сложность 1–10:')); layout.addWidget(self.difficulty)
        layout.addWidget(QLabel('Теги:')); layout.addWidget(self.tags_input)
        layout.addWidget(QLabel('Контесты:')); layout.addWidget(self.contest_list)
        layout.addWidget(QLabel('Примечание:')); layout.addWidget(self.note)

        hl = QHBoxLayout()
        hl.addWidget(btn_save)
        hl.addWidget(btn_cancel)
        layout.addLayout(hl)

        self.setLayout(layout)

        if task is not None:
            self.load_task(task)

    def load_task(self, task):
        self.title.setText(task.title or '')
        self.description.setPlainText(task.description or '')
        self.solution.setPlainText(task.solution_idea or '')
        self.polygon.setText(task.polygon_url or '')
        self.prepared_cf.setChecked(bool(task.prepared_cf))
        self.prepared_yandex.setChecked(bool(task.prepared_yandex))
        self.difficulty.setValue(task.difficulty or 1)
        self.note.setPlainText(task.note or '')
        self.tags_input.setText(','.join([t.name for t in task.tags]))

        contest_ids = [c.id for c in task.contests]
        for i in range(self.contest_list.count()):
            item = self.contest_list.item(i)
            if item.data(Qt.UserRole) in contest_ids:
                item.setCheckState(Qt.Checked)

    def save(self):
        if self.read_only:
            return

        title = self.title.text().strip()
        if not title:
            QMessageBox.warning(self, 'Ошибка', 'У задачи должно быть название')
            return

        data = {
            'title': title,
            'description': self.description.toPlainText(),
            'solution_idea': self.solution.toPlainText(),
            'polygon_url': self.polygon.text().strip(),
            'prepared_cf': self.prepared_cf.isChecked(),
            'prepared_yandex': self.prepared_yandex.isChecked(),
            'difficulty': self.difficulty.value(),
            'note': self.note.toPlainText()
        }

        s = Session()
        try:
            if self.task is None:
                t = Task(**data)
                s.add(t)
            else:
                t = s.query(Task).get(self.task.id)
                for k,v in data.items():
                    setattr(t, k, v)

            # Теги
            t.tags = []
            tags_text = self.tags_input.text().strip()
            if tags_text:
                for tn in [x.strip() for x in tags_text.split(',') if x.strip()]:
                    tag = s.query(Tag).filter_by(name=tn).first()
                    if not tag:
                        tag = Tag(name=tn)
                        s.add(tag)
                        s.flush()
                    t.tags.append(tag)

            # Контесты
            selected_contests = []
            for i in range(self.contest_list.count()):
                item = self.contest_list.item(i)
                if item.checkState() == Qt.Checked:
                    cid = item.data(Qt.UserRole)
                    c = s.query(Contest).get(cid)
                    selected_contests.append(c)
            t.contests = selected_contests

            if t.polygon_url:
                t.prepared_cf = True

            s.commit()
            self.accept()
        except Exception as e:
            s.rollback()
            QMessageBox.critical(self, 'Ошибка', str(e))
        finally:
            s.close()