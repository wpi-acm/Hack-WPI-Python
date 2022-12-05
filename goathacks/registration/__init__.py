from datetime import datetime
from flask import Blueprint, flash, render_template, request
import flask_login
from flask_login import current_user
from goathacks.registration.forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash

from goathacks import db
from goathacks.models import User

bp = Blueprint('registration', __name__, url_prefix="/registration")

@bp.route("/")
def register():
    if current_user.is_authenticated:
        flash("You are already registered and logged in!")

    form = RegisterForm(request.form)
    if request.method == 'POST' and form.validate():
        email = request.form.get('email')
        first_name = request.form.get('first_name')
        last_name = request.form.get('last_name')
        password = request.form.get('password')
        password_c = request.form.get('password_confirm')


        if password == password_c:
            # Passwords match!
            user = User(
                    email=email,
                    password=generate_password_hash(password),
                    first_name=first_name,
                    last_name=last_name,
                    last_login=datetime.now(),
            )

            db.session.add(user)
            db.session.commit()
            flask_login.login_user(user)

            return "OK"
        else:
            flash("Passwords do not match")

    return render_template("register.html", form=form)
