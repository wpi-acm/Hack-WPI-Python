from flask import flash, redirect, url_for
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, DateTime, Integer, String
from . import db
from . import login

class User(db.Model, UserMixin):
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    last_login = Column(DateTime, nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    is_admin = Column(Boolean, nullable=False, default=False)
    waitlisted = Column(Boolean, nullable=False, default=False)


@login.user_loader
def user_loader(user_id):
    return User.query.filter_by(id=user_id).first()

@login.unauthorized_handler
def unauth():
    flash("Please login first")
    return redirect(url_for("registration.register"))
