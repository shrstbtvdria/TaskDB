from sqlalchemy import Column, Integer, String, Boolean, Text, Table, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

task_tag = Table(
    "task_tag",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.id"), primary_key=True)
)

task_contest = Table(
    "task_contest",
    Base.metadata,
    Column("task_id", Integer, ForeignKey("tasks.id"), primary_key=True),
    Column("contest_id", Integer, ForeignKey("contests.id"), primary_key=True)
)

class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True)
    title = Column(String, nullable=False)
    description = Column(Text)
    solution_idea = Column(Text)
    polygon_url = Column(String)
    prepared_cf = Column(Boolean, default=False)
    prepared_yandex = Column(Boolean, default=False)
    difficulty = Column(Integer, default=1)
    note = Column(Text)

    tags = relationship("Tag", secondary=task_tag, back_populates="tasks")
    contests = relationship("Contest", secondary=task_contest, back_populates="tasks")

class Tag(Base):
    __tablename__ = "tags"
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    tasks = relationship("Task", secondary=task_tag, back_populates="tags")

class Contest(Base):
    __tablename__ = "contests"
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    year = Column(Integer)
    tasks = relationship("Task", secondary=task_contest, back_populates="contests")
