# coding: utf-8
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, text, Float
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from werkzeug.security import generate_password_hash, check_password_hash

Base = declarative_base()
metadata = Base.metadata


class Event(Base):
    __tablename__ = 'event'

    id = Column(Integer, primary_key=True)
    organization = Column(ForeignKey(u'organization.id'), nullable=False, index=True)
    check_in = Column(DateTime)
    check_out = Column(DateTime)
    user_rfid = Column(String(45), nullable=False)
    total_minutes = Column(Float)

    organization1 = relationship(u'Organization')


class Organization(Base):
    __tablename__ = 'organization'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    password = Column(String(100), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)


class User(Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    name = Column(String(45), nullable=False)
    organization = Column(ForeignKey(u'organization.id'), nullable=False, index=True)
    rfid = Column(String(45))
    role = Column(Integer)
    password = Column(String(100), nullable=False)

    def set_password(self, password):
        self.password = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password, password)

    organization1 = relationship(u'Organization')
