from flask import Flask
from os import environ
from dontbudge.api.routes import api
from dontbudge.auth.routes import auth
from dontbudge.dashboard import dashboard
from dontbudge import database

SECRET = environ.get('FLASK_SECRET_KEY')
DEBUG = environ.get('DONTBUDGE_DEBUG')

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True if DEBUG else False
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///../db/dontbudge.sqlite3'
    app.config['SECRET_KEY'] = SECRET
    app.register_blueprint(api)
    app.register_blueprint(auth)
    app.register_blueprint(dashboard)
    database.init_app(app)
    return app