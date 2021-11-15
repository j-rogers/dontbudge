from flask import Flask
from dontbudge.api.routes import api

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    app.register_blueprint(api)
    return app