import flask
from flask import Response, render_template, redirect, request, url_for, flash, current_app
from flask_login import current_user, login_required
from goathacks.admin import bp, forms
from goathacks import db
from goathacks.models import Event

import io, qrcode, datetime
import qrcode.image.pure

@bp.route("/events")
@login_required
def list_events():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    events = Event.query.all()

    form = forms.EventForm()

    return render_template("events/list.html", events=events, form=form)

@bp.route("/event/<int:id>/delete")
@login_required
def delete_event(id):
    if not current_user.is_admin:
        return {"status": "error", "message": "Unauthorized"}
    
    event = Event.query.filter_by(id=id).first()

    if event is None:
        return {"status": "error", "message": "Invalid event ID"}
    
    db.session.delete(event)
    db.session.commit()

    return {"status": "success"}

@bp.route("/event/<int:id>")
@login_required
def event(id):
    if not current_user.is_admin:
        return {"status": "error", "message": "Unauthorized"}
    
    event = Event.query.filter_by(id=id).first()

    if event is None:
        return {"status": "error", "message": "Invalid event ID"}
    
    return event.create_json()

@bp.route("/event/<int:id>", methods=["POST"])
@login_required
def update_create_event(id):
    if not current_user.is_admin:
        flash("Unauthorized")
        return redirect(url_for("dashboard.home"))

    name = request.form.get('name')
    description = request.form.get('description')
    location = request.form.get('location')
    start_day = request.form.get('start_day')
    start_time = request.form.get('start_time')
    end_day = request.form.get('end_day')
    end_time = request.form.get('end_time')
    start = datetime.datetime.combine(datetime.date.fromisoformat(start_day),
                              datetime.time.fromisoformat(start_time)) 
    end = datetime.datetime.combine(datetime.date.fromisoformat(end_day),
                                  datetime.time.fromisoformat(end_time)) 

    if id == 0:
        # new event
        e = Event(
                name=name,
                description=description,
                location=location,
                start_time=start,
                end_time=end)
        db.session.add(e)
        db.session.commit()
        current_app.logger.info(f"{current_user} is creating a new event: {e.name}")
    else:
        e = Event.query.filter_by(id=id).first()
        if e is None:
            return {"status": "error", "message": "Invalid event ID"}
        e.name = name
        e.description = description
        e.location = location
        e.start_time = start
        e.end_time = end
        db.session.commit()
        current_app.logger.info(f"{current_user} is updating an existing event: {e.name}")


    return redirect(url_for("admin.list_events"))

@bp.route("/events/events.json")
@login_required
def events_json():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))
    events = Event.query.all()
    return Event.create_json_output(events)

@bp.route("/events/new", methods=["GET", "POST"])
@login_required
def new_event():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    form = forms.EventForm(request.form)
    if request.method == 'POST':
        name = request.form.get("name")
        description = request.form.get("description")
        location = request.form.get("location")
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
        category = request.form.get("category")

        event = Event(
                name = name,
                description = description,
                location = location,
                start_time = start_time,
                end_time = end_time,
                category = category
                )

        db.session.add(event)
        db.session.commit()
        flash("Created event")
        return redirect(url_for("admin.list_events"))
        

    return render_template("events/new_event.html", form=form)

@bp.route("/events/edit/<int:id>", methods=["GET", "POST"])
@login_required
def edit_event(id):
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    event = Event.query.filter_by(id=id).one()
    if event is None:
        flash("Event does not exist")
        return redirect(url_for("admin.list_events"))

    form = forms.EventForm(request.form)
    if request.method == 'POST':
        form.populate_obj(event) 
        db.session.commit()
        flash("Updated event")
        return redirect(url_for("admin.list_events"))
    else:
        form = forms.EventForm(obj=event)

    return render_template("events/new_event.html", form=form)

@bp.route("/events/qrcode/<int:id>")
@login_required
def qrcode_event(id):
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    event = Event.query.filter_by(id=id).first()
    if event is None:
        flash("Event does not exist")
        return redirect(url_for("admin.list_events")) 

    return render_template("events/qrcode.html", event=event)
