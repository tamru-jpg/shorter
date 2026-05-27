from flask import Blueprint, render_template
from flask_login import login_required

bp = Blueprint('main', __name__)


@bp.route('/')
def index():
    """Главная страница для неавторизованных пользователей"""
    return render_template('index.html')


@bp.route('/main')
@login_required
def main():
    """Главная страница с формой сокращения ссылок (только для авторизованных)"""
    return render_template('main.html')
