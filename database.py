from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SQLALCHEMY_DATABASE_URL = "mysql+mysqlconnector://collab_admin:collab@chat@localhost/collab_db"

engine = create_engine( SQLALCHEMY_DATABASE_URL )

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)