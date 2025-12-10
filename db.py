import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from models import Base, Task, Tag, Contest
import config
from sqlalchemy.exc import IntegrityError

DB_PATH = config.DB_PATH
DB_DIR = os.path.dirname(DB_PATH)
if DB_DIR and not os.path.exists(DB_DIR):
    os.makedirs(DB_DIR, exist_ok=True)

engine = create_engine(f"sqlite:///{DB_PATH}", echo=False, connect_args={"check_same_thread": False})
Session = scoped_session(sessionmaker(bind=engine))

def init_db():
    Base.metadata.create_all(engine)

def add_sample_data():
    s = Session()
    try:
        if s.query(Tag).count() == 0:
            t1 = Tag(name='mod')
            t2 = Tag(name='ascii-art')
            t3 = Tag(name='formula')
            s.add_all([t1,t2,t3])
        if s.query(Contest).count() == 0:
            c1 = Contest(name='Python 5-7 Start', year=2025)
            c2 = Contest(name='10 TX Операции с числами', year=2025)
            c3 = Contest(name='Python 5-7 Самостоятельная работа', year=2024)
            s.add_all([c1,c2,c3])
        s.commit()
        if s.query(Task).count() == 0:
            task = Task(title='Пример: сумма чисел', description='Дается список...', solution_idea='Просто сложить', difficulty=3, prepared_cf=False)
            task.tags.append(s.query(Tag).filter_by(name='strings').first())
            task.contests.append(s.query(Contest).first())
            s.add(task)
            s.commit()
    except IntegrityError:
        s.rollback()
    finally:
        s.close()

from sqlalchemy.orm import joinedload

def get_all_tasks():
    s = Session()
    try:
        tasks = (
            s.query(Task)
            .options(
                joinedload(Task.tags),
                joinedload(Task.contests)
            )
            .order_by(Task.id)
            .all()
        )
        return tasks
    finally:
        s.close()


def add_task(**kwargs):
    s = Session()
    try:
        t = Task(**kwargs)
        if t.polygon_url:
            t.prepared_cf = True
        s.add(t)
        s.commit()
        return t
    except Exception as e:
        s.rollback()
        raise
    finally:
        s.close()

def update_task(task_id, **kwargs):
    s = Session()
    try:
        t = s.query(Task).get(task_id)
        for k,v in kwargs.items():
            setattr(t, k, v)
        if t.polygon_url:
            t.prepared_cf = True
        s.commit()
        return t
    except Exception as e:
        s.rollback()
        raise
    finally:
        s.close()

def delete_task(task_id):
    s = Session()
    try:
        t = s.query(Task).get(task_id)
        s.delete(t)
        s.commit()
    finally:
        s.close()

def get_all_tags():
    s = Session()
    try:
        return s.query(Tag).order_by(Tag.name).all()
    finally:
        s.close()

def get_or_create_tag(name):
    s = Session()
    try:
        tag = s.query(Tag).filter_by(name=name).first()
        if not tag:
            tag = Tag(name=name)
            s.add(tag)
            s.commit()
        return tag
    finally:
        s.close()

def get_all_contests():
    s = Session()
    try:
        return s.query(Contest).order_by(Contest.year.desc()).all()
    finally:
        s.close()

def add_tag(name):
    s = Session()
    try:
        tag = Tag(name=name)
        s.add(tag)
        s.commit()
        return tag
    except IntegrityError:
        s.rollback()
        raise
    finally:
        s.close()

def add_contest(name, year):
    s = Session()
    try:
        c = Contest(name=name, year=year)
        s.add(c)
        s.commit()
        return c
    finally:
        s.close()

def filter_tasks(min_diff=1, max_diff=10, tag_names=None):
    s = Session()
    try:
        q = s.query(Task)
        q = q.filter(Task.difficulty >= min_diff, Task.difficulty <= max_diff)
        if tag_names:
            q = q.join(Task.tags).filter(Tag.name.in_(tag_names)).group_by(Task.id).having(func.count(Task.id) >= len(tag_names))
        return q.all()
    finally:
        s.close()

def get_task_with_relations(task_id):
    s = Session()
    try:
        task = (
            s.query(Task)
            .options(
                joinedload(Task.tags),
                joinedload(Task.contests)
            )
            .filter(Task.id == task_id)
            .first()
        )
        return task
    finally:
        s.close()
