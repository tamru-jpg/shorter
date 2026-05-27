from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app.db import db
from app.models import User

bp = Blueprint('auth', __name__)


@bp.route('/login', methods=['GET', 'POST'])
def login():
    """Авторизация пользователя: форма входа и обработка данных"""
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember_me = request.form.get('remember_me') == 'on'

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=remember_me)
            flash('Вы успешно вошли!', 'success')
            return redirect(url_for('main.main'))
        else:
            flash('Неверный email или пароль', 'danger')

    return render_template('login.html')


@bp.route('/register', methods=['GET', 'POST'])
def register():
    """Регистрация нового пользователя: форма и сохранение в БД"""
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        password_check = request.form.get('password_check')
        if password != password_check:
            flash('Пароли не совпадают!', 'danger')
            return render_template('reg.html')

        if len(password) < 6:
            flash('Пароль должен быть не менее 6 символов', 'danger')
            return render_template('reg.html')

        if User.query.filter_by(email=email).first():
            flash('Этот email уже зарегистрирован', 'danger')
            return render_template('reg.html')

        user = User(username=username, email=email)
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        flash('Регистрация успешна! Теперь войдите', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reg.html')


@bp.route('/logout')
@login_required
def logout():
    """Выход пользователя из системы"""
    logout_user()
    flash('Вы вышли из системы', 'info')
    return redirect(url_for('main.index'))


@bp.route('/profile')
@login_required
def profile():
    """Личный кабинет пользователя: отображение данных профиля"""
    return render_template('lk.html', user=current_user)
