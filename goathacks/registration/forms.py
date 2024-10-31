from flask_wtf import FlaskForm
from wtforms import BooleanField, IntegerField, PasswordField, SelectField, StringField, SubmitField, widgets
from wtforms.validators import DataRequired
import os

class RegisterForm(FlaskForm):
    __location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))
    schools_list = open(os.path.join(__location__, 'schools.txt')).read().split("\n")
    countries_list = open(os.path.join(__location__, 'countries.csv')).read().split("\n")

    email = StringField("Email", validators=[DataRequired()])
    first_name = StringField("Preferred First Name",
                             validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    password_confirm = PasswordField("Confirm Password",
                                     validators=[DataRequired()])
    school = SelectField("School", choices=[(school, school) for school in schools_list], widget=widgets.Select())
    phone_number = StringField("Phone number", validators=[DataRequired()])
    age = IntegerField("Age", validators=[DataRequired()])
    dietary_restrictions = StringField("Dietary Restrictions (Optional)")
    gender = SelectField("Gender", choices=[("F", "Female"), ("M", "Male"),
                                            ("NB", "Non-binary/Other")],
                         widget=widgets.Select())
    country = SelectField("Country", choices=[(country.split(",")[0], country.split(",")[0]) for country in countries_list], widget=widgets.Select())
    newsletter = BooleanField("Subscribe to the MLH newsletter?")
    agree_coc = BooleanField("I confirm that I have read and agree to the Code of Conduct", validators=[DataRequired()])
    logistics = BooleanField("I authorize you to share my application/registration with Major League Hacking for event administration, ranking, and MLH administration in-line with the MLH privacy policy.I further agree to the terms of both the MLH Contest Terms and Conditions and the MLH Privacy Policy.", validators=[DataRequired()])

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
