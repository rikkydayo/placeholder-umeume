from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class TemplateForm(FlaskForm):
    template = TextAreaField('Template', validators=[DataRequired()])
    params = TextAreaField('Parameters', validators=[DataRequired()])
    submit = SubmitField('Submit')