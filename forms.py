from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class LoginForm(FlaskForm):
    username = StringField('ユーザ名', validators=[DataRequired()])
    password = PasswordField('パスワード', validators=[DataRequired()])
    submit = SubmitField('ログイン')

class TemplateForm(FlaskForm):
    template = TextAreaField('テンプレート', validators=[DataRequired()])
    params = TextAreaField('パラメータ', validators=[DataRequired()])
    submit = SubmitField('生成！')