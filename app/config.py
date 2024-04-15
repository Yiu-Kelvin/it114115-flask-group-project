import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config(object):
    SECRET_KEY = os.environ.get("SECRET_KEY") or "you-will-never-guess"
    # SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL") or 'mysql+pymysql://flaskuser:1234@flask-db:3306/flaskdb'
    if os.environ.get('testdb') == "True": 
        SQLALCHEMY_DATABASE_URI = "sqlite://"
    else:
        SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://flaskuser:1234@flask-db:3306/flaskdb'

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or "mailhog"
    MAIL_PORT = int(os.environ.get('MAIL_PORT') or 1025)
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    ADMINS = ['flask@pikaamail.com']
    POSTS_PER_PAGE = 3
    TAGS_PER_PAGE = 36
    LANGUAGES = ['en', 'es', 'zh']
