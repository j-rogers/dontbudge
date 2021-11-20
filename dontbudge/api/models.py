from sqlalchemy.orm import relationship
from dontbudge.database import db

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    name = db.Column(db.String(50))
    occurence = db.Column(db.Integer)

    def __init__(self, start, name, occurence, user_id):
        self.start = start
        self.name = name
        self.occurence = occurence
        self.user_id = user_id

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    period_id = db.Column(db.Integer, db.ForeignKey('periods.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    description = db.Column(db.String(100))
    date = db.Column(db.DateTime)

    def __init__(self, period_id, account_id, description, date, bill_id=None):
        self.period_id = period_id
        self.account_id = account_id
        self.description = description
        self.date = date
        self.bill_id = bill_id

class Period(db.Model):
    __tablename__ = 'periods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)
    transactions = relationship('Transaction', backref='period')

    def __init__(self, start, end, user_id):
        self.start = start
        self.end = end
        self.user_id = user_id

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    name = db.Column(db.String(100))
    balance = db.Column(db.Integer)
    
    def __init__(self, name, balance, user_id):
        self.name = name
        self.balance = balance
        self.user_id = user_id

class UserDetails(db.Model):
    __tablename__ = 'userdetails'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(15))
    range = db.Column(db.Integer)
    accounts = relationship('Account', backref='user')
    periods = relationship('Period', backref='user')
    bills = relationship('Bill', backref='user')

    def __init__(self, name, range=14):
        self.name = name
        self.range = range
