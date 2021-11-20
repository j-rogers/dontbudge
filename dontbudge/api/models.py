from sqlalchemy.orm import relationship
from dontbudge.database import db

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    user_id_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    name = db.Column(db.String(50))
    occurence = db.Column(db.Integer)

    def __init__(self, start, name, occurence, user):
        self.start = start
        self.name = name
        self.occurence = occurence
        self.user = user

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('periods.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    description = db.Column(db.String(100))
    date = db.Column(db.DateTime)

    def __init__(self, period, account, description, date, bill=None):
        self.period = period
        self.account = account
        self.description = description
        self.date = date
        self.bill = bill

class Period(db.Model):
    __tablename__ = 'periods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    transactions = relationship('Transaction', backref='period')

    def __init__(self, start, end, user):
        self.start = start
        self.end = end
        self.user = user

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    name = db.Column(db.String(100))
    balance = db.Column(db.Integer)
    
    def __init__(self, name, balance, user):
        self.name = name
        self.balance = balance
        self.user = user

class UserDetails(db.Model):
    __tablename__ = 'userdetails'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    range = db.Column(db.Integer)
    accounts = relationship('Account', backref='user')
    periods = relationship('Period', backref='user')
    bills = relationship('Bill', backref='user')

    def __init__(self, user_id, name, range=14):
        self.name = name
        self.range = range
