from sqlmodel import SQLModel, create_engine, Session
from sqlalchemy import event



sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)

# Enforces Foreign Key constraints
event.listen(engine, 'connect', lambda c, _: c.execute('pragma foreign_keys=on'))

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    
def get_session():
    with Session(engine) as session:
        yield session