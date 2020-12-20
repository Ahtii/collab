from sqlalchemy import (
    Boolean, Column, Integer, REAL, TIMESTAMP,
    String, Table, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.sql import expression
from sqlalchemy.ext.compiler import compiles
from sqlalchemy.types import DateTime
from datetime import datetime
import pytz

Base = declarative_base()

# for many to many relationship
user_room = Table('user_room', Base.metadata,
                  Column('user_id', Integer, ForeignKey('user.id')),
                  Column('room_id', Integer, ForeignKey('room.id'))
                  )    
# function to generate utc datetime for database
class utcnow(expression.FunctionElement):
    type = DateTime()

@compiles(utcnow, 'mysql')
def my_utcnow(element, compiler, **kw):
    return "UTC_TIMESTAMP()"                      

class Profile(Base):

    __tablename__ = "profile"
    
    id = Column(Integer, primary_key=True)
    designation = Column(String(50), default="intern")
    avatar = Column(String(500), nullable=True)
    bio = Column(String(500), nullable=True)         
    user = relationship("User", uselist=False, backref="profile")

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
    created_date = Column(TIMESTAMP, default=utcnow())
    modified_date = Column(TIMESTAMP, default=utcnow())
    is_social_account = Column(Boolean, default=False)
    room = relationship("Room", secondary=user_room, backref='participants', lazy='dynamic')
    profile = Column(Integer, ForeignKey("profile.id"))

class Room(Base):

    __tablename__ = "room"

    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    description = Column(String(200))
    created_date = Column(TIMESTAMP, default=datetime.utcnow())
    admin = Column(String(50))  # link to use model
    is_default = Column(Boolean, default=False)

    def get_admin(self):
        return self.admin


class BaseMessage(object):

    id = Column(Integer, primary_key=True)
    created_date = Column(TIMESTAMP, default=utcnow())
    modified_date = Column(TIMESTAMP, default=utcnow())
    text = Column(Text(500))
    attachment_url = Column(String(500), nullable=True)


class PersonalMessage(BaseMessage, Base):

    __tablename__ = "personal_message"

    sender_id = Column(Integer, ForeignKey('user.id'))
    receiver_id = Column(Integer, ForeignKey('user.id'))


class RoomMessage(BaseMessage, Base):

    __tablename__ = "room_message"

    sender_id = Column(Integer, ForeignKey('user.id'))
    room_id = Column(Integer, ForeignKey('room.id'))