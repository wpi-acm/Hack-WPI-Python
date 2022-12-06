from flask import Blueprint, flash, render_template, request
from flask_login import current_user, login_required

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

from goathacks.dashboard import forms
from goathacks import db

@bp.route("/", methods=["GET", "POST"])
@login_required
def home():
    form = forms.ShirtAndAccomForm(request.form)
    if request.method == "POST" and form.validate():
        current_user.shirt_size = request.form.get('shirt_size')
        current_user.accomodations = request.form.get('accomodations')
        db.session.commit()
        flash("Updated successfully")
    return render_template("dashboard.html", form=form)
