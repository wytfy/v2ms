from flask import Blueprint, render_template, redirect, url_for, flash
from flask_login import login_required, login_user, logout_user, current_user
from forms.form import LoginForm
from models.Rooter import Rooter

auth = Blueprint('auth', __name__)


@auth.route('/')
def home():
    return redirect(url_for('auth.login'))


@auth.route('/login', methods=['GET', 'POST'])
def login():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = Rooter.query.filter_by(username=login_form.username.data).first()
        if user is not None and user.verify_password(login_form.password.data):
            login_user(user, login_form.remember_me.data)
            return redirect(url_for('v2ms_bp.user_list'))
        flash('无效的用户名或密码')
    if current_user.is_authenticated:
        return redirect(url_for('v2ms_bp.user_list'))
    return render_template('login.html', login_form=login_form)


@auth.route('/secret')
@login_required
def secret():
    return 'Only authenticated users are allowed!'


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('退出登录')
    return redirect(url_for('auth.login'))


# 404处理
@auth.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
