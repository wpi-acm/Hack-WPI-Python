from flask_wtf import FlaskForm
from wtforms import StringField, DateTimeField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    location = StringField("Location", validators=[DataRequired()])
    start_time = DateTimeField("Start Time", validators=[DataRequired()])
    end_time = DateTimeField("End Time", validators=[DataRequired()])
    category = StringField("Category")
    submit = SubmitField("Submit")
