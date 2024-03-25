from flask_wtf import FlaskForm
from wtforms import SubmitField

class UpdateImagesForm(FlaskForm):
    submit = SubmitField('Capture Images')
