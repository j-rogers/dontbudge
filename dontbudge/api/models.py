from dontbudge.database import db

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    period = db.Column(db.Integer, foreign_key=True)
    account = db.Column(db.Integer, foreign_key=True)

    def __init__(self, period, account):
        self.period = period
        self.account = account

class Period(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, foreign_key=True)
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __init__(self, start, end, user):
        self.start = start
        self.end = end
        self.user = user

class Account(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    balance = db.Column(db.Integer)
    user = db.Column(db.Integer, foreign_key=True)

    def __init__(self, name, balance, user):
        self.name = name
        self.balance = balance
        self.user = user

class UserDetails(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    range = db.Column(db.Integer)

    def __init__(self, name, range=14):
        self.name = name
        self.range = range
