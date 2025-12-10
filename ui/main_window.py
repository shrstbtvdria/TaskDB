from PyQt5.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QSpinBox, QLineEdit, QTableWidget, QTableWidgetItem, QFileDialog, QMessageBox
from db import init_db, add_sample_data, get_all_tasks, delete_task, get_all_tags, get_all_contests, Session
from ui.task_dialog import TaskDialog
from models import Task, Tag, Contest
import csv, os

class MainWindow(QMainWindow):
    def __init__(self, is_admin=False):
        super().__init__()
        self.setWindowTitle('TaskDB — база задач')
        self.resize(900,600)
        self.is_admin = is_admin

        central = QWidget()
        main_layout = QVBoxLayout()

        # Фильтры
        hl_filter = QHBoxLayout()
        self.min_diff = QSpinBox(); self.min_diff.setRange(1,10); self.min_diff.setValue(1)
        self.max_diff = QSpinBox(); self.max_diff.setRange(1,10); self.max_diff.setValue(10)
        self.tag_filter = QLineEdit(); self.tag_filter.setPlaceholderText('Теги через запятую')
        btn_filter = QPushButton('Применить фильтр')
        btn_clear = QPushButton('Сбросить фильтр')

        hl_filter.addWidget(QLabel('Сложность от:')); hl_filter.addWidget(self.min_diff)
        hl_filter.addWidget(QLabel('до:')); hl_filter.addWidget(self.max_diff)
        hl_filter.addWidget(self.tag_filter)
        hl_filter.addWidget(btn_filter); hl_filter.addWidget(btn_clear)
        main_layout.addLayout(hl_filter)

        # Таблица
        self.table = QTableWidget(0,6)
        self.table.setHorizontalHeaderLabels(['ID','Название','Сложность','Codeforces','Теги','Контесты'])
        self.table.setColumnHidden(0, True)
        self.table.setSelectionBehavior(self.table.SelectRows)
        main_layout.addWidget(self.table)

        # Кнопки
        hl_buttons = QHBoxLayout()
        self.btn_add = QPushButton('Добавить')
        self.btn_edit = QPushButton('Редактировать')
        self.btn_delete = QPushButton('Удалить')
        self.btn_view = QPushButton('Просмотреть')
        self.btn_export = QPushButton('Экспорт CSV')

        # Скрываем админ-кнопки для обычного пользователя
        if not self.is_admin:
            self.btn_add.setVisible(False)
            self.btn_edit.setVisible(False)
            self.btn_delete.setVisible(False)

        hl_buttons.addWidget(self.btn_add)
        hl_buttons.addWidget(self.btn_edit)
        hl_buttons.addWidget(self.btn_delete)
        hl_buttons.addWidget(self.btn_view)
        hl_buttons.addWidget(self.btn_export)
        main_layout.addLayout(hl_buttons)

        central.setLayout(main_layout)
        self.setCentralWidget(central)

        # Сигналы
        btn_filter.clicked.connect(self.apply_filter)
        btn_clear.clicked.connect(self.load_tasks)
        self.btn_add.clicked.connect(self.add_task)
        self.btn_edit.clicked.connect(self.edit_task)
        self.btn_delete.clicked.connect(self.delete_task)
        self.btn_view.clicked.connect(self.view_task)
        self.btn_export.clicked.connect(self.export_csv)

        # Инициализация базы
        init_db()
        add_sample_data()
        self.load_tasks()
        
    # Методы
    def load_tasks(self):
        self.table.setRowCount(0)
        tasks = get_all_tasks()
        for t in tasks:
            self._append_task_row(t)

    def _append_task_row(self, t):
        row = self.table.rowCount()
        self.table.insertRow(row)
        self.table.setItem(row,0, QTableWidgetItem(str(t.id)))
        self.table.setItem(row,1, QTableWidgetItem(t.title or ''))
        self.table.setItem(row,2, QTableWidgetItem(str(t.difficulty or '')))
        self.table.setItem(row,3, QTableWidgetItem('Да' if t.prepared_cf else 'Нет'))
        self.table.setItem(row,4, QTableWidgetItem(','.join([ta.name for ta in t.tags])))
        self.table.setItem(row,5, QTableWidgetItem(','.join([c.name for c in t.contests])))

    def get_selected_task_id(self):
        sel = self.table.selectedItems()
        if not sel:
            return None
        row = sel[0].row()
        item = self.table.item(row,0)
        return int(item.text())

    # Методы админа
    def add_task(self):
        if not self.is_admin:
            QMessageBox.warning(self, 'Доступ запрещён', 'Нет прав для добавления')
            return
        dlg = TaskDialog(self)
        if dlg.exec():
            self.load_tasks()

    def edit_task(self):
        if not self.is_admin:
            QMessageBox.warning(self, 'Доступ запрещён', 'Нет прав для редактирования')
            return
        tid = self.get_selected_task_id()
        if not tid:
            QMessageBox.information(self, 'Инфо', 'Выберите задачу')
            return
        from db import get_task_with_relations
        task = get_task_with_relations(tid)
        if not task:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить задачу')
            return
        dlg = TaskDialog(self, task=task)
        if dlg.exec():
            self.load_tasks()

    def delete_task(self):
        if not self.is_admin:
            QMessageBox.warning(self, 'Доступ запрещён', 'Нет прав для удаления')
            return
        tid = self.get_selected_task_id()
        if not tid:
            QMessageBox.information(self, 'Инфо', 'Выберите задачу')
            return
        from db import delete_task
        if QMessageBox.question(self, 'Подтвердить', 'Удалить задачу?') == QMessageBox.Yes:
            delete_task(tid)
            self.load_tasks()

    # Просмотр задачи для всех
    def view_task(self):
        tid = self.get_selected_task_id()
        if not tid:
            QMessageBox.information(self, 'Инфо', 'Выберите задачу')
            return
        from db import get_task_with_relations
        task = get_task_with_relations(tid)
        if not task:
            QMessageBox.warning(self, 'Ошибка', 'Не удалось загрузить задачу')
            return
        dlg = TaskDialog(self, task=task, read_only=True)
        dlg.exec()

    # Фильтры
    def apply_filter(self):
        min_d = self.min_diff.value()
        max_d = self.max_diff.value()
        tag_list = [x.strip() for x in self.tag_filter.text().split(',') if x.strip()]
        self.table.setRowCount(0)
        tasks = get_all_tasks()
        for t in tasks:
            if t.difficulty < min_d or t.difficulty > max_d:
                continue
            if tag_list:
                names = [ta.name for ta in t.tags]
                if not all(x in names for x in tag_list):
                    continue
            self._append_task_row(t)

    # Экспорт CSV
    def export_csv(self):
        path, _ = QFileDialog.getSaveFileName(
            self, 'Сохранить CSV', os.path.join('reports','tasks_export.csv'), 'CSV Files (*.csv)'
        )
        if not path:
            return
        rows = []
        for r in range(self.table.rowCount()):
            tid = self.table.item(r,0).text()
            title = self.table.item(r,1).text()
            diff = self.table.item(r,2).text()
            prepared = self.table.item(r,3).text()
            tags = self.table.item(r,4).text()
            contests = self.table.item(r,5).text()
            rows.append([tid, title, diff, prepared, tags, contests])
        try:
            with open(path, 'w', encoding='utf-8-sig', newline='') as f:
                writer = csv.writer(f, delimiter=';')  # Excel-friendly
                writer.writerow(['id','title','difficulty','prepared_cf','tags','contests'])
                writer.writerows(rows)
            QMessageBox.information(self, 'Экспорт', f'Экспорт выполнен: {path}')
        except Exception as e:
            QMessageBox.critical(self, 'Ошибка', str(e))