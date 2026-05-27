from flask import Flask, render_template
from flask_login import LoginManager
from dotenv import load_dotenv
import os

load_dotenv()
from app.db import db

login_manager = LoginManager()


def create_app():
    """Создание и настройка экземпляра Flask"""
    app = Flask(__name__, template_folder='../templates', static_folder='../static')

    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-key')
    app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///../instance/shorter.db')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user_id):
        """Загружает пользователя по ID из сессии"""
        from app.models import User
        return db.session.get(User, int(user_id))

    from app.routes import main, auth, links
    app.register_blueprint(main.bp)
    app.register_blueprint(auth.bp)
    app.register_blueprint(links.bp)

    @app.errorhandler(404)
    def not_found_error(error):
        """Страница 404 - не найдено"""
        return render_template('errors/404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Страница 500 - внутренняя ошибка сервера"""
        db.session.rollback()
        return render_template('errors/500.html'), 500

    with app.app_context():
        db.create_all()

    return app
