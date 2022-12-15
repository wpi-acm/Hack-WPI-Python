

from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from . import db

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False)
    is_admin = Column(Boolean, nullable=False, default=False)
