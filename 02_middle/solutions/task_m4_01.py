"""
Рішення — Урок 4 (Databases)

Дивись після того, як спробував сам!
"""
import os
from sqlalchemy import create_engine, Column, Integer, String, Boolean, select
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()
DB_PATH = os.path.join(os.path.dirname(__file__), "tasks.db")


class Task(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    completed = Column(Boolean, default=False)


def main() -> None:
    engine = create_engine(f"sqlite:///{DB_PATH}")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        session.add(Task(title="Задача 1", completed=False))
        session.add(Task(title="Задача 2", completed=False))
        session.commit()

        tasks = session.execute(select(Task)).scalars().all()
        for t in tasks:
            print(f"{t.id}: {t.title} - {t.completed}")

        first = session.execute(select(Task).where(Task.id == 1)).scalars().first()
        first.completed = True
        session.commit()
        print("Оновлено:", first.title, first.completed)


if __name__ == "__main__":
    main()
