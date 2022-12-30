from datetime import datetime
from flask import Blueprint, config, current_app, flash, redirect, render_template, request, url_for
import flask_login
from flask_login import current_user
from goathacks.registration.forms import LoginForm, RegisterForm
from werkzeug.security import check_password_hash, generate_password_hash
from flask_mail import Message

from goathacks import db, mail as app_mail
from goathacks.models import User

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
            db.session.add(user)
            db.session.commit()
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

        if check_password_hash(user.password, password):
            flask_login.login_user(user)

            flash("Welcome back!")

            return redirect(url_for("dashboard.home"))
        else:
            flash("Incorrect password")

    return render_template("login.html", form=form)
