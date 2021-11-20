from dontbudge.database import db

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    userdetails_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))

    def __init__(self, userdetails_id, username, password):
        self.userdetails_id = userdetails_id
        self.username = username
        self.password = password