from flask import Blueprint, current_app, flash, redirect, url_for
from flask_login import current_user, login_required

from goathacks.models import Event, EventCheckins
from goathacks import db

bp = Blueprint("events", __name__, url_prefix="/events")

@bp.route("/checkin/<int:id>")
@login_required
def workshop_checkin(id):
    event = Event.query.filter_by(id=id).one()
    if event is None:
        flash("That event does not exist!")
        return redirect(url_for("dashboard.home"))

    checkin = EventCheckins.query.filter_by(event_id=id,
                                            user_id=current_user.id).first()
    if checkin is not None:
        flash("You've already checked into this event!")
        return redirect(url_for("dashboard.home"))

    checkin = EventCheckins(
            user_id=current_user.id,
            event_id=id
            )
    db.session.add(checkin)
    db.session.commit()

    flash("You've successfully checked in!")
    return redirect(url_for("dashboard.home"))
