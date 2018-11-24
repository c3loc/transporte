#! /usr/bin/env python

from flask import Flask

from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

from flask_mail import Mail

from flask_login import LoginManager

from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

app = Flask(__name__)

app.config.from_pyfile('config.cfg')

db = SQLAlchemy(app)
migrate = Migrate(app, db)

limiter = Limiter(app, key_func=get_remote_address)

mail = Mail(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

from .views import *

login_manager.user_loader(load_user)


if __name__ == '__main__':
    app.run('0.0.0.0', debug=app.config['DEBUG'])
