from flask import Flask, request, render_template, redirect, url_for, flash, session
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user
import re
import os
import logging
from datetime import timedelta
from html import escape
from forms import LoginForm, TemplateForm
from flask_bcrypt import Bcrypt

# ロギング設定
log_level = os.environ.get('LOG_LEVEL', 'DEBUG')
logging.basicConfig(level=getattr(logging, log_level))
logger = logging.getLogger(__name__)

app = Flask(__name__)
bcrypt = Bcrypt(app)

# 環境変数チェック
try:
    app.secret_key = os.environ['FLASK_SECRET_KEY']  # 環境変数必須
    USERS = {k: v for k, v in [pair.split(':') for pair in os.environ['USERS'].split(',')]}
except KeyError as e:
    logger.error(f"Missing environment variable: {e}")
    raise RuntimeError(f"Environment variable {e} is not set. Please set FLASK_SECRET_KEY and USERS.")
except Exception as e:
    logger.error(f"Failed to parse USERS: {e}")
    raise RuntimeError(f"Failed to parse USERS: {e}")

# セッション設定
app.permanent_session_lifetime = timedelta(minutes=90)
app.config.update(
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    WTF_CSRF_ENABLED=True
)

# Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login' #type: ignore

class User(UserMixin):
    def __init__(self, username):
        self.id = username

@login_manager.user_loader
def load_user(username):
    return User(username) if username in USERS else None

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if username in USERS and bcrypt.check_password_hash(USERS[username], password):
            user = User(username)
            login_user(user)
            flash('ログイン成功！', 'success')
            return redirect(url_for('index'))
        flash('ユーザー名またはパスワードが間違っています。', 'error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()  # セッション全体をクリア
    flash('ログアウトしました。', 'success')
    return redirect(url_for('login'))

@app.route('/', methods=['GET', 'POST'])
@login_required
def index():
    form = TemplateForm()
    result = None
    if form.validate_on_submit() and form.submit.data:
        template = form.template.data
        params = form.params.data
        if not template:
            result = "エラー: テンプレートを入力してください。"
        elif not params:
            result = "エラー: パラメータを入力してください。"
        else:
            result = create_formatted_sql(template, params)
    return render_template('index.html', form=form, result=result)

def create_formatted_sql(template, params):
    try:
        param_list = [p.strip() for p in params.split(',') if p.strip()]
        if not param_list:
            return "エラー: パラメータが空です。"
        
        placeholder_count = template.count('?')
        if placeholder_count != len(param_list):
            return f"エラー: プレースホルダ（?）の数（{placeholder_count}）とパラメータの数（{len(param_list)}）が一致しません。"
        
        formatted_params = []
        for param in param_list:
            match = re.match(r'(.+)\((Integer|LocalDate|String|BigDecimal|LocalDateTime|Boolean|NULL)\)$', param)
            if not match:
                return f"エラー: パラメータの形式が不正です: {param}"
            value, param_type = match.groups()
            if param_type in ['Integer', 'BigDecimal']:
                formatted_params.append(value)
            elif param_type in ['LocalDate', 'String']:
                formatted_params.append(f"'{value}'")
            elif param_type == 'LocalDateTime':
                value = value.replace('T', ' ')
                formatted_params.append(f"'{value}'")
            elif param_type == 'Boolean':
                formatted_params.append(value.upper())
            elif param_type == 'NULL':
                formatted_params.append('NULL')
            else:
                return f"エラー: サポートされていない型です: {param_type}"
        
        result = template
        for param in formatted_params:
            result = result.replace('?', param, 1)
        return result
    except Exception as e:
        return f"エラー: {str(e)}"

@app.after_request
def add_security_headers(response):
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self'; style-src 'self'"
    return response

if __name__ == '__main__':
    app.run(debug=False)