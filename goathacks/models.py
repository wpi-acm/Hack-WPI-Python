from flask import flash, redirect, url_for
from flask_login import UserMixin
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, String
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

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
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
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
    expires = Column(DateTime, nullable=False)


"""
Represents an event within the hackathon, that can be checked into
"""
class Event(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    location = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    category = Column(String, nullable=True)

    def create_json_output(lis):
        events = []

        for e in lis:
            events.append(e.create_json())

        return events
    
    def create_json(self):
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "location": self.location,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat(),
            "category": self.category
        }

    def get_checkins(self):
        checkins = EventCheckins.query.filter_by(event_id=self.id).all()

        return checkins
        


class EventCheckins(db.Model):
    __tablename__ = "event_checkins"
    id = Column(Integer, primary_key=True)
    event_id = Column(Integer, ForeignKey('event.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('user.id'), nullable=False)
