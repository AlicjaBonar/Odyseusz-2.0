import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.database.database import DATABASE_NAME


def print_usage():
    print("Usage: python create_database.py")
    sys.exit(1)



def init_database():
    engine = create_engine(f"sqlite:///{DATABASE_NAME}.db", echo=True)
    Session = sessionmaker(bind=engine, autoflush=True)
    Base.metadata.create_all(engine)
    return engine, Session


if __name__ == "__main__":
    engine, Session = init_database()

    print("Created tables:", Base.metadata.tables.keys())