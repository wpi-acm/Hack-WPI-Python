from flask_wtf import FlaskForm
from wtforms import StringField, DateField, TimeField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class EventForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    description = TextAreaField("Description")
    location = StringField("Location", validators=[DataRequired()])
    start_day = DateField("Start Day", validators=[DataRequired()])
    start_time = TimeField("Start Time", validators=[DataRequired()])
    end_day = DateField("End Day", validators=[DataRequired()])
    end_time = TimeField("End Time", validators=[DataRequired()])
    category = StringField("Category")
    submit = SubmitField("Submit")
