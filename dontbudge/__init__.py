from flask import Flask
from os import environ
from dontbudge.api.routes import api
from dontbudge.auth.routes import auth
from dontbudge import database

SECRET = environ.get('FLASK_SECRET_KEY')

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dontbudge.sqlite3'
    app.config['SECRET_KEY'] = SECRET
    app.register_blueprint(api)
    app.register_blueprint(auth)
    database.init_app(app)
    return app