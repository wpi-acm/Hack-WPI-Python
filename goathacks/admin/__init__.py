from flask import Blueprint, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from flask_mail import Message

from goathacks.models import User

bp = Blueprint("admin", __name__, url_prefix="/admin")

from goathacks import db, mail as app_mail
from goathacks.admin import events

@bp.route("/")
@login_required
def home():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))
    male_count = 0
    female_count = 0
    nb_count = 0
    check_in_count = 0
    waitlist_count = 0
    total_count = 0
    shirt_count = {'XS': 0, 'S': 0, 'M': 0, 'L': 0, 'XL': 0}
    hackers = db.session.execute(db.select(User)).scalars().all()
    schools = {}
    
    for h in hackers:
        if h.waitlisted:
            waitlist_count += 1

        if h.checked_in:
            check_in_count += 1

        if h.gender == 'F':
            female_count += 1
        elif h.gender == 'M':
            male_count += 1
        else:
            nb_count += 1

        total_count += 1

        if h.school not in schools:
            schools[h.school] = 1
        else:
            schools[h.school] += 1

        if h.shirt_size not in shirt_count:
            shirt_count[h.shirt_size] = 1
        else:
            shirt_count[h.shirt_size] += 1
    return render_template("admin.html", waitlist_count=waitlist_count,
                           total_count=total_count, shirt_count=shirt_count,
                           hackers=hackers, male_count=male_count,
                           female_count=female_count, nb_count=nb_count,
                           check_in_count=check_in_count, schools=schools)

@bp.route("/mail")
@login_required
def mail():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    total_count = len(db.session.execute(db.select(User)).scalars().all())

    return render_template("mail.html", NUM_HACKERS=total_count)

@bp.route("/send", methods=["POST"])
@login_required
def send():
    if not current_user.is_admin:
        return {"status": "error"}

    json = request.json

    users = User.query.all()

    to = []
    if json["recipients"] == "org":
        to = ["hack@wpi.edu"]
    elif json['recipients'] == 'admin':
        to = ["acm-sysadmin@wpi.edu"]
    elif json['recipients'] == "all":
        to = [x.email for x in users]

    with app_mail.connect() as conn:
        for e in to:
            msg = Message(json['subject'])
            msg.add_recipient(e)
            msg.html = json['html']
            msg.body = json['text']

            conn.send(msg)

    return {"status": "success"}

@bp.route("/check_in/<int:id>")
@login_required
def check_in(id):
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    user = User.query.filter_by(id=id).one()
    if user is None:
        return {"status": "error", "msg": "No user found"}
    user.checked_in = True
    db.session.commit()
    return {"status": "success"}

@bp.route("/drop/<int:id>")
@login_required
def drop(id):
    if not current_user.is_admin and not current_user.id == id:
        return redirect(url_for("dashboard.home"))

    user = User.query.filter_by(id=id).one()
    if user is None:
        return {"status": "error", "msg": "user not found"}

    if user.checked_in:
        return {"status": "error", "msg": "Hacker is already checked in"}

    msg = Message("Application Dropped")
    msg.add_recipient(user.email)
    msg.sender = ("GoatHacks Team", "hack@wpi.edu")
    msg.body = render_template("emails/dropped.txt", user=user)
    app_mail.send(msg)

    db.session.delete(user)
    db.session.commit()

    return {"status": "success"}

@bp.route("/change_admin/<int:id>/<string:action>")
@login_required
def change_admin(id, action):
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    user = User.query.filter_by(id=id).one() 
    if user is None:
        return {"status": "error", "msg": "user not found"}



    valid_actions = ['promote', 'demote']
    if action not in valid_actions:
        return {"status": "error", "msg": "invalid action"}

    if action == "promote":
        user.is_admin = True
    else:
        user.is_admin = False

    db.session.commit()

    return {"status": "success"}

@bp.route("/promote_from_waitlist/<int:id>")
@login_required
def promote_waitlist(id):
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    user = User.query.filter_by(id=id).one()
    if user is None:
        return {"status": "error", "msg": "user not found"}

    user.waitlisted = False
    db.session.commit()

    msg = Message("Waitlist Promotion")
    msg.add_recipient(user.email)
    msg.sender = ("GoatHacks Team", "hack@wpi.edu")
    msg.body = render_template("emails/waitlist_promotion.txt", user=user)
    mail.send(msg)

    return {"status": "success"}

@bp.route("/hackers.csv")
@login_required
def hackers_csv():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    users = User.query.all()
    return json_to_csv(User.create_json_output(users))

@bp.route("/hackers")
@login_required
def hackers():
    if not current_user.is_admin:
        return redirect(url_for("dashboard.home"))

    users = User.query.all()
    return User.create_json_output(users)

import json
import csv
from io import StringIO
 
 
def json_to_csv(data):
    # Opening JSON file and loading the data
    # into the variable data
    
    json_data=[]
    if(type(data) is json):
        json_data=data
    elif(type(data) is str):
        json_data=json.loads(data)
    else:
        json_data = json.loads(json.dumps(data))
    # now we will open a file for writing
    csv_out = StringIO("")
    
    # create the csv writer object
    csv_writer = csv.writer(csv_out)
    
    # Counter variable used for writing
    # headers to the CSV file
    count = 0
    
    for e in json_data:
        if count == 0:
    
            # Writing headers of CSV file
            header = e.keys()
            csv_writer.writerow(header)
            count += 1
    
        # Writing data of CSV file
        csv_writer.writerow(e.values())
    csv_out.seek(0)
    return csv_out.read()
