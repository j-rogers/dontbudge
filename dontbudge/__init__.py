from flask import Flask
from dontbudge.api.routes import api
from dontbudge import database

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///dontbudge.sqlite3'
    app.register_blueprint(api)
    database.init_app(app)
    return app