import flask
from flask import Response, render_template, redirect, request, url_for, flash
from flask_login import current_user, login_required
from goathacks.admin import bp, forms
from goathacks import db
from goathacks.models import Event

import io, qrcode
import qrcode.image.pure

@bp.route("/events")
@login_required
def list_events():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    events = Event.query.all()

    form = forms.EventForm()

    return render_template("events/list.html", events=events, form=form)

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
