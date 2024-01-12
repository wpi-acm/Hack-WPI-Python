from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import SelectField, TextAreaField, SubmitField
from wtforms.validators import DataRequired

class ShirtAndAccomForm(FlaskForm):
    shirt_size = SelectField("Shirt size", choices=["XS", "S", "M", "L", "XL",
                                                   "None"],
                            validators=[DataRequired()])
    accomodations = TextAreaField("Special needs and/or Accomodations")
    submit = SubmitField("Save")

class ResumeForm(FlaskForm):
    resume = FileField("Resume", validators=[FileRequired(),
                                             FileAllowed(['pdf', 'docx', 'doc',
                                                          'txt', 'rtf'],
                                                         "Documents only!")])

    submit = SubmitField("Submit")
