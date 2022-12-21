from flask import Flask, redirect, render_template, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
from flask_assets import Bundle, Environment
from flask_cors import CORS
from flask_mail import Mail


db = SQLAlchemy()
migrate = Migrate()
login = LoginManager()
environment = Environment()
cors = CORS()
mail = Mail()

def create_app():
    app = Flask(__name__)

    app.config.from_pyfile("config.py")

    db.init_app(app)
    migrate.init_app(app, db)
    login.init_app(app) 
    environment.init_app(app)
    cors.init_app(app)
    mail.init_app(app)

    scss = Bundle('css/style.scss', filters='scss',
    output='css/style.css')
    environment.register('scss', scss)

    from .models import User

    from . import registration
    from . import dashboard
    from . import admin

    app.register_blueprint(registration.bp)
    app.register_blueprint(dashboard.bp)
    app.register_blueprint(admin.bp)


    from goathacks import cli
    app.cli.add_command(cli.gr)


    #Sponsor page
    @app.route("/sponsor")
    def sponsorindex():
        return render_template('home/sponsor/index.html')
    
    @app.route('/sponsor/<path:path>')
    def sponsor(path):
        return send_from_directory('templates/home/sponsor', path)

    #Code of conduct 
    @app.route('/conduct/conduct.pdf')
    def conduct():
        return url_for('template/home/conduct/', filename='conduct.pdf')

    # Homepage
    @app.route("/")
    def index_redirect():
        return redirect("/index.html")
    @app.route("/index.html")
    def index():
        return render_template("home/index.html")

    # homepage assets
    @app.route("/assets/<path:path>")
    def assets(path):
        return send_from_directory('templates/home/assets', path)

    return app


