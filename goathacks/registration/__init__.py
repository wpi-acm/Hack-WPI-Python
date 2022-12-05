from flask import Blueprint, flash
from flask_login import current_user


bp = Blueprint('registration', __name__, url_prefix="/registration")

@bp.route("/")
def register():
    if current_user.is_authenticated:
        flash("You are already registered and logged in!")


