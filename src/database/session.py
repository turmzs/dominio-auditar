import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session, declarative_base

# Resolve o path do SQLite de forma determinística (evita "sqlite_master vazio" por DB relativo ./)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # .../src
PROJECT_DIR = os.path.dirname(BASE_DIR)  # .../DOMINIO-AUDITAR
DATABASE_FILE = os.path.join(PROJECT_DIR, 'fiscal_erp.db')
DATABASE_URL = f'sqlite:///{DATABASE_FILE.replace("\\", "/")}'

engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
session_factory = sessionmaker(bind=engine)
Session = scoped_session(session_factory)
Base = declarative_base()

def get_session():
    return Session()