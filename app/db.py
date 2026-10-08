from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

engine = create_engine("postgresql+psycopg://postgres:devpass@localhost:5432/ccmonitor")
SessionLocal = sessionmaker(engine)


class Base(DeclarativeBase):
    pass


def get_db():
    with SessionLocal() as db:
        yield db
