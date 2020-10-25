from sqlalchemy import Boolean, Column, Integer, String, Date
import database

class User(database.Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True, nullable=False)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(300), nullable=False)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_date = Column(Date, nullable=True)
    modified_date = Column(Date, nullable=True)



