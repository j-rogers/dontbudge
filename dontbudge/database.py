"""Database

Provides an SQLAlchemy ORM object for interacting with the database.

Author: Josh Rogers (2021)
"""
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_app(app):
    """Initialises the SQLAlchemy instance with the Flask app"""
    db.init_app(app)
    db.create_all(app=app)