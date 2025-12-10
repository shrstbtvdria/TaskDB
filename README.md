# TaskDB — приложение баз данных для ведения базы данных задач по программированию

Это учебный проект (шаблон) настольного приложения на Python + PyQt5 + SQLite + SQLAlchemy.
Приложение реализует:
- Модели: задачи, теги, контесты, связи многие-ко-многим.
- CRUD для задач/тегов/контестов.
- Фильтрация по сложности и тегам.
- Два уровня доступа: админ (логин/пароль) и гость (просмотр);
- Экспорт отчёта в CSV.

## Как запустить на Windows
1. Установите Python 3.8+, при установке поставьте галочку "Add Python to PATH";
2. Распакуйте проект и откройте папку в терминале;
3. Создайте и активируйте виртуальное окружение:
```
python -m venv venv
venv\Scripts\activate
```
4. Установите зависимости:
```
pip install -r requirements.txt
```
5. Инициализируйте базу и запустите приложение:
```
python -c "import db; db.init_db()"
python main.py
```
6. Данные для входа (администратор): `admin` / `admin`. Можно изменить в файле `config.py`.

## Структура проекта
```
TaskDB/
├─ main.py
├─ db.py
├─ models.py
├─ config.py
├─ requirements.txt
├─ README.md
├─ database/taskdb.sqlite3
├─ ui/
│  ├─ main_window.py
│  ├─ login_window.py
│  ├─ task_dialog.py
│  ├─ tag_dialog.py
│  ├─ contest_dialog.py
```