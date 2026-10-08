from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase

engine = create_engine("postgresql+psycopg://postgres:devpass@localhost:5432/ccmonitor")


class Base(DeclarativeBase):
    pass