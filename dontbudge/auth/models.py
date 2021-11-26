from sqlalchemy.orm import relationship
from dontbudge.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    userdetails = relationship('UserDetails', uselist=False, backref='user')

    def __init__(self, username, password):
        self.username = username
        self.password = password