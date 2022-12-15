from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import RadioField, TextAreaField
from wtforms.validators import DataRequired

class ShirtAndAccomForm(FlaskForm):
    shirt_size = RadioField("Shirt size", choices=["XS", "S", "M", "L", "XL",
                                                   "None"],
                            validators=[DataRequired()])
    accomodations = TextAreaField("Special needs and/or Accomodations")

class ResumeForm(FlaskForm):
    resume = FileField("Resume", validators=[FileRequired(),
                                             FileAllowed(['pdf', 'docx', 'doc',
                                                          'txt', 'rtf'],
                                                         "Documents only!")])
