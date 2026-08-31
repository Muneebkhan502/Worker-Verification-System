from sqlalchemy.orm import sessionmaker, DeclarativeBase
from sqlalchemy import create_engine

SQLALCHEMY_DATABASE_URL = "postgresql://postgres:admin1234@Localhost:5433/Worker_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit = False, autoflush = False, bind = engine)

class Base(DeclarativeBase):
    pass

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
