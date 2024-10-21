from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, SelectField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired
import os

class RegisterForm(FlaskForm):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    schools_list = open(os.path.join(__location__, 'schools.txt')).read().split("\n")

    email = StringField("Email", validators=[DataRequired()])
    first_name = StringField("Preferred First Name",
                             validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirm = PasswordField("Confirm Password",
                                     validators=[DataRequired()])
    school = SelectField("School", choices=[(school, school) for school in schools_list], widget=widgets.Select())
    phone_number = StringField("Phone number", validators=[DataRequired()])
    gender = SelectField("Gender", choices=[("F", "Female"), ("M", "Male"),
                                            ("NB", "Non-binary/Other")],
                         widget=widgets.Select())
    agree_coc = BooleanField("I confirm that I have read and agree to the Code of Conduct", validators=[DataRequired()])

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Sign in")

class ResetForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    submit = SubmitField("Request reset")

class PwResetForm(FlaskForm):
    password = PasswordField("Password")
    password_confirm = PasswordField("Confirm Password")
    submit = SubmitField("Submit")
