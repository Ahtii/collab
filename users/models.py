from sqlalchemy import (
    Boolean, Column, Integer,
    String, Date, Table, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# for many to many relationship
user_room = Table('user_room', Base.metadata,
                  Column('user_id', Integer, ForeignKey('user.id')),
                  Column('room_id', Integer, ForeignKey('room.id'))
                  )


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True)
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
    room = relationship("Room", secondary=user_room, backref='participants', lazy='dynamic')


class Room(Base):
    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    admin = Column(String(50))  # link to use model

    def get_admin(self):
        return self.admin

# class Message(Base):
#     id = Column(Integer, primary_key=True)
#     created_date = Column(Date)
#     modified_date = Column(Date, nullable=True)
#     text = Column(Text(300))
#     attachment = Column(Binary)
#     owner = Column(User)

