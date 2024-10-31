import os

from dotenv import load_dotenv, dotenv_values

basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, '.env'))

class Config():
    TESTING = dotenv_values().get("TESTING") or False
    DEBUG = dotenv_values().get("DEBUG") or False

    SQLALCHEMY_DATABASE_URI = dotenv_values().get("SQLALCHEMY_DATABASE_URI") or "postgresql://localhost/goathacks"

    MAX_BEFORE_WAITLIST = int(dotenv_values().get("MAX_BEFORE_WAITLIST")) or 1
    MCE_API_KEY = dotenv_values().get("MCE_API_KEY")
    SECRET_KEY = dotenv_values().get("SECRET_KEY") or "bad-key-change-me"

    UPLOAD_FOLDER = dotenv_values().get("UPLOAD_FOLDER") or "./uploads/"

    DISCORD_LINK = dotenv_values().get("DISCORD_LINK") or None

    # Mail server settings
    MAIL_SERVER = dotenv_values().get("MAIL_SERVER") or "localhost"
    MAIL_PORT = dotenv_values().get("MAIL_PORT") or 25
    MAIL_USE_TLS = dotenv_values().get("MAIL_USE_TLS") or False
    MAIL_USE_SSL = dotenv_values().get("MAIL_USE_SSL") or False
    MAIL_USERNAME = dotenv_values().get("MAIL_USERNAME") or "dummy"
    MAIL_PASSWORD = dotenv_values().get("MAIL_PASSWORD") or "dummy"
    MAIL_DEFAULT_SENDER = dotenv_values().get("MAIL_DEFAULT_SENDER") or "GoatHacks Team <hack@wpi.edu>"
    MAIL_SUPPRESS_SEND = dotenv_values().get("MAIL_SUPPRESS_SEND") or TESTING
