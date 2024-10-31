from flask import Blueprint, current_app, flash, jsonify, redirect, render_template, request, url_for
from flask_login import current_user, login_required
from werkzeug.utils import secure_filename

import os

bp = Blueprint("dashboard", __name__, url_prefix="/dashboard")

from goathacks.dashboard import forms
from goathacks import db

@bp.route("/", methods=["GET", "POST"])
@login_required
def home():
    form = forms.ShirtAndAccomForm(request.form)
    resform = forms.ResumeForm(request.form)
    if request.method == "POST" and form.validate():
        current_user.shirt_size = request.form.get('shirt_size')
        current_user.accomodations = request.form.get('accomodations')
        db.session.commit()
        flash("Updated successfully")
    else:
        form = forms.ShirtAndAccomForm(obj=current_user)
    return render_template("dashboard.html", form=form, resform=resform)

@bp.route("/resume", methods=["POST"])
@login_required
def resume():
    form = forms.ResumeForm(request.form)

    """A last minute hack to let people post their resume after they've already registered"""
    if request.method == 'POST':
        if 'resume' not in request.files:
            return "You tried to submit a resume with no file"

        resume = request.files['resume']
        if resume.filename == '':
            return "You tried to submit a resume with no file"

        if resume and not allowed_file(resume.filename):
            return jsonify(
                {'status': 'error', 'action': 'register',
                 'more_info': 'Invalid file type... Accepted types are txt pdf doc docx and rtf...'})

        if resume and allowed_file(resume.filename):
            # Good file!
            filename = current_user.first_name.lower() + '_' + current_user.last_name.lower() + '_' + str(
                current_user.id) + '.' + resume.filename.split('.')[-1].lower()
            filename = secure_filename(filename)
            if not os.path.exists(current_app.config['UPLOAD_FOLDER']):
                try:
                    os.makedirs(current_app.config['UPLOAD_FOLDER'])
                except Exception:
                    flash("Error saving resume. Contact acm-sysadmin@wpi.edu")
                    return redirect(url_for("dashboard.home"))
            resume.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
            flash("Resume uploaded!")
            return redirect(url_for("dashboard.home"))
    flash("Something went wrong. If this keeps happening, contact hack@wpi.edu for assistance")
    return redirect(url_for("dashboard.home"))


def allowed_file(filename):
    return '.' in filename and \
           filename.split('.')[-1].lower() in ['pdf', 'docx', 'doc', 'txt',
                                               'rtf']
