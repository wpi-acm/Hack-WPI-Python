from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py")

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app) 

    from .models import User

    return app
