from decimal import Decimal
from datetime import date
from sqlalchemy.orm import relationship
from dontbudge.database import db

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    name = db.Column(db.String(50))
    occurence = db.Column(db.String(4))
    amount = db.Column(db.Numeric(scale=2))

    def __init__(self, start: date, name: str, occurence: str, user_id: int, amount: Decimal):
        self.start = start
        self.name = name
        self.occurence = occurence
        self.user_id = user_id
        self.amount = amount

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.Integer)

    def __init__(self, name: str):
        self.name = name

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    description = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Numeric(scale=2))

    def __init__(self, account_id: int, description: str, date: date, amount: Decimal, bill_id: int = None):
        self.account_id = account_id
        self.description = description
        self.date = date
        self.amount = amount
        self.bill_id = bill_id

class Period(db.Model):
    __tablename__ = 'periods'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    end = db.Column(db.DateTime)

    def __init__(self, start: date, end: date, user_id: int):
        self.start = start
        self.end = end
        self.user_id = user_id

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    name = db.Column(db.String(100))
    balance = db.Column(db.Numeric(scale=2))
    transactions = relationship('Transaction', backref='account')

    def __init__(self, name: str, balance: Decimal, user_id: id):
        self.name = name
        self.balance = balance
        self.user_id = user_id

class UserDetails(db.Model):
    __tablename__ = 'userdetails'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(15))
    range = db.Column(db.Integer)
    accounts = relationship('Account', backref='user')
    periods = relationship('Period', backref='user')
    bills = relationship('Bill', backref='user')

    def __init__(self, name: str, user_id: int, range: int = 14):
        self.name = name
        self.user_id = user_id
        self.range = range
