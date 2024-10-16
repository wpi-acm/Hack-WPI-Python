from datetime import datetime, timedelta
from flask import Blueprint, abort, config, current_app, flash, redirect, render_template, request, url_for
import flask_login
from flask_login import current_user, login_required
from goathacks.registration.forms import LoginForm, PwResetForm, RegisterForm, ResetForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message
import ulid
from sqlalchemy.exc import IntegrityError

from goathacks import db, mail as app_mail
from goathacks.models import PwResetRequest, User

bp = Blueprint('registration', __name__, url_prefix="/registration")

@bp.route("/", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        flash("You are already registered and logged in!")

    print("got register")
    form = RegisterForm(request.form)
    print(vars(form.gender))
    if request.method == 'POST':
        print("Got form")
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        password_c = request.form.get('password_confirm')
        school = request.form.get('school')
        phone = request.form.get('phone_number')
        gender = request.form.get('gender')


        if password == password_c:
            # Passwords match!

            # Count of all non-waitlisted hackers
            num_not_waitlisted = len(User.query.filter_by(waitlisted=False).all())
            waitlisted = False
            print(num_not_waitlisted)
            print(current_app.config['MAX_BEFORE_WAITLIST'])
            if num_not_waitlisted >= current_app.config['MAX_BEFORE_WAITLIST']:
                waitlisted = True
            user = User(
                    email=email,
                    password=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    last_login=datetime.now(),
                    waitlisted=waitlisted,
                    school=school,
                    phone=phone,
                    gender=gender
            )

            #try to add the user to the database, checking for duplicate users
            try:
                db.session.add(user)
                db.session.commit()
            except IntegrityError as err:
                db.session.rollback()
                if "duplicate key value violates unique constraint" in str(err):
                    flash("User with email " + email + " already exists.")
                else:
                    flash("An unknown error occurred.")
                return redirect(url_for("registration.login"))

            #user successfully registered, so login
            flask_login.login_user(user)

            if waitlisted:
                msg = Message("Goathacks - Waitlist Confirmation")
            else:
                msg = Message("GoatHacks - Registration Confirmation")

            msg.add_recipient(user.email)
            msg.sender = ("GoatHacks Team", "hack@wpi.edu")
            msg.body = render_template("emails/registration.txt", user=user)
            app_mail.send(msg)

            return redirect(url_for("dashboard.home"))
        else:
            flash("Passwords do not match")

    return render_template("register.html", form=form)

@bp.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm(request.form)

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user == None:
            flash("Email or password incorrect")
            return render_template("login.html", form=form)

        if check_password_hash(user.password, password):
            flask_login.login_user(user)

            flash("Welcome back!")

            return redirect(url_for("dashboard.home"))
        else:
            flash("Incorrect password")

    return render_template("login.html", form=form)

@bp.route("/logout")
@login_required
def logout():
    flask_login.logout_user()
    flash("See you later!")
    return redirect(url_for("registration.login"))

@bp.route("/reset", methods=["GET", "POST"])
def reset():
    form = ResetForm(request.form)

    if request.method == 'POST':
        email = request.form.get('email')

        user = User.query.filter_by(email=email).first()

        if user == None:
            flash("If that email has an account here, we've just sent it a link to reset your password.")
            return redirect(url_for("registration.login"))
        else:
            r = PwResetRequest(
                    id=str(ulid.ulid()),
                    user_id=user.id,
                    expires=datetime.now() + timedelta(minutes=30)
                    )
            
            db.session.add(r)
            db.session.commit()

            msg = Message("GoatHacks - Password Reset Request")
            msg.add_recipient(user.email)
            msg.body = render_template("emails/password_reset.txt", code=r.id)
            app_mail.send(msg)
            flash("If that email has an account here, we've just sent it a link to reset your password.")
            return redirect(url_for("registration.login"))

    else:
        return render_template("pw_reset.html", form=form)

@bp.route("/reset/complete/<string:id>", methods=["GET", "POST"])
def do_reset(id):
    form = PwResetForm(request.form)
    req = PwResetRequest.query.filter_by(id=id).first()

    if req == None:
        flash("Invalid request")
        return redirect(url_for("registration.login"))

    if req.expires < datetime.now():
        db.session.delete(req)
        db.session.commit()
        flash("Invalid request")
        return redirect(url_for("registration.login"))

    if request.method == "POST":
        password = request.form.get("password")
        password_c = request.form.get("password_confirm")

        if password == password_c:
            user = User.query.filter_by(id=req.user_id).first()
            if user == None:
                flash("Invalid user")
                return redirect(url_for("registration.login"))
            user.password = generate_password_hash(password)
            db.session.delete(req)
            db.session.commit()
            flash("Password successfully reset")
            return redirect(url_for("registration.login"))
        else:
            flash("Passwords do not match!")
            return render_template("password_reset.html", form=form)
    else:
        return render_template("password_reset.html", form=form)
