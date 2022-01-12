from decimal import Decimal
from datetime import date
from sqlalchemy.orm import relation, relationship
from dontbudge.database import db

class Bill(db.Model):
    __tablename__ = 'bills'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    start = db.Column(db.DateTime)
    name = db.Column(db.String(50))
    occurence = db.Column(db.String(4))
    amount = db.Column(db.Numeric(scale=2))
    transactions = relationship('Transaction', backref='bill')

    def __init__(self, start: date, name: str, occurence: str, user_id: int, amount: Decimal):
        self.start = start
        self.name = name
        self.occurence = occurence
        self.user_id = user_id
        self.amount = amount

class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    name = db.Column(db.Integer)
    amount = db.Column(db.Numeric(scale=2))
    transactions = relationship('Transaction', backref='budget')

    def __init__(self, name: str, user_id: int, amount: Decimal):
        self.name = name
        self.user_id = user_id
        self.amount = amount

class Category(db.Model):
    __tablename__ = 'categories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    name = db.Column(db.Integer)
    transactions = relationship('Transaction', backref='category')

    def __init__(self, name: str, user_id: int):
        self.name = name
        self.user_id = user_id

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id'))
    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'))
    bill_id = db.Column(db.Integer, db.ForeignKey('bills.id'))
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'))
    budget_id = db.Column(db.Integer, db.ForeignKey('budgets.id'))
    description = db.Column(db.String(100))
    date = db.Column(db.DateTime)
    amount = db.Column(db.Numeric(scale=2))

    def __init__(self, user_id: int, account_id: int, description: str, date: date, amount: Decimal, bill_id: int = None, category_id: int = None, budget_id: int = None):
        self.user_id = user_id
        self.account_id = account_id
        self.description = description
        self.date = date
        self.amount = amount
        self.bill_id = bill_id
        self.category_id = category_id
        self.budget_id = budget_id

class Account(db.Model):
    __tablename__ = 'accounts'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('userdetails.id', ondelete='CASCADE'))
    name = db.Column(db.String(100))
    balance = db.Column(db.Numeric(scale=2))
    transactions = relationship('Transaction', backref='account', cascade='delete')

    def __init__(self, name: str, balance: Decimal, user_id: id):
        self.name = name
        self.balance = balance
        self.user_id = user_id

class UserDetails(db.Model):
    __tablename__ = 'userdetails'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    name = db.Column(db.String(15))
    range = db.Column(db.String(4))
    period_start = db.Column(db.DateTime)
    period_end = db.Column(db.DateTime)
    accounts = relationship('Account', backref='user', cascade='delete')
    bills = relationship('Bill', backref='user', cascade='delete')
    categories = relationship('Category', backref='user', cascade='delete')
    budgets = relationship('Budget', backref='user', cascade='delete')
    transactions = relationship('Transaction', backref='user', cascade='delete')

    def __init__(self, name: str, user_id: int, range: str, period_start: date, period_end: date):
        self.name = name
        self.user_id = user_id
        self.range = range
        self.period_start = period_start
        self.period_end = period_end
