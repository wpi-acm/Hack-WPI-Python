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
    shirt_size = Column(String, nullable=True)
    accomodations = Column(String, nullable=True)
    checked_in = Column(Boolean, nullable=False, default=False)
    school = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    gender = Column(String, nullable=True)

    def create_json_output(lis):
        hackers = []

        for u in lis:
            hackers.append({
                'checked_in': u.checked_in,
                'waitlisted': u.waitlisted,
                'admin': u.is_admin,
                'id': u.id,
                'email': u.email,
                'first_name': u.first_name,
                'last_name': u.last_name,
                'phone_number': u.phone,
                'shirt_size': u.shirt_size,
                'special_needs': u.accomodations,
                'school': u.school
                })

        return hackers


@login.user_loader
def user_loader(user_id):
    return User.query.filter_by(id=user_id).first()

@login.unauthorized_handler
def unauth():
    flash("Please login first")
    return redirect(url_for("registration.register"))


class PwResetRequest(db.Model):
    id = Column(String, primary_key=True)
    user_id = db.relationship("User")
