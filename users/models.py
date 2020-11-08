from sqlalchemy import Boolean, Column, Integer, String, Date
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class User(Base):

    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(50), nullable=False)
    last_name = Column(String(50), nullable=False)
    username = Column(String(50), nullable=False)
    email = Column(String(255), nullable=False)
    password = Column(String(300), nullable=False)
    is_active = Column(Boolean, default=False)
    is_verified = Column(Boolean, default=False)
    created_date = Column(Date, nullable=True)
    modified_date = Column(Date, nullable=True)
    is_social_account = Column(Boolean, default=False)

# class Room(Base):
#
#     __tablename__ = "room"
#
#     id = Column(Integer, primary_key=True, index=True)
#     name = Column(String(50), nullable=False)
#     description = Column(String(200))
#     subscribers = Column(String, nullable=False)
#
#     def set_subscribers(self, subscriber):
#         subscribers = self.subscribers
#         if subscribers:
#             subscribers += "," + subscriber
#         else:
#             subscribers = subscriber
#         self.subscribers = subscribers
#
#     def get_subscribers(self):
#         subscribers = self.subscribers
#         if subscribers:
#             return subscribers.split(",")
#         else:
#             return None

