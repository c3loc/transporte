from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail

from flask_login import LoginManager

db = SQLAlchemy()
mail = Mail()
login_manager = LoginManager()


def create_app():
    """Construct the core application."""
    app = Flask(__name__)
    app.config.from_pyfile('config.cfg')
    db.init_app(app)
    mail.init_app(app)
    login_manager.init_app(app)

    with app.app_context():
        from . import views  # noqa: F401
        db.create_all()

        return app
