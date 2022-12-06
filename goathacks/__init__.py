from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_assets import Bundle, Environment


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
environment = Environment()

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py")

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app) 
    environment.init_app(app)

    scss = Bundle('css/style.scss', filters='scss',
    output='css/style.css')
    environment.register('scss', scss)

    from .models import User

    from . import registration
    from . import dashboard

    app.register_blueprint(registration.bp)
    app.register_blueprint(dashboard.bp)

    return app
