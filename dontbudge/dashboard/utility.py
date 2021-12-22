from collections import namedtuple
from datetime import date
from dateutil.relativedelta import relativedelta
from dontbudge.database import db
from dontbudge.api.models import Category

Transaction = namedtuple('Transaction', [
    'amount',
    'description',
    'category',
    'account_name',
    'date',
    'transaction_index',
    'account_index'
])

Period = namedtuple('Period', [
    'start',
    'end'
])

Bill = namedtuple('Bill', [
    'name',
    'amount',
    'start',
    'occurence',
    'bill_index'
])

Menu = namedtuple('Menu', [
    'title',
    'items'
])

MenuItem = namedtuple('MenuTuple', [
    'title',
    'link'
])

def get_relative(code):
    switch = {
        '1W': relativedelta(weeks=1),
        '2W': relativedelta(weeks=2),
        '1M': relativedelta(months=1),
        '1Q': relativedelta(months=3),
        '1Y': relativedelta(years=1)
    }

    return switch.get(code)

def get_sorted_transactions(userdetails, account=None):
    transactions = []
    if account:
        for transaction in account.transactions:
            category = Category.query.filter_by(id=transaction.category_id).first()
            category_name = category.name if category else 'None'
            transactions.append(Transaction(
                transaction.amount,
                transaction.description,
                category_name,
                account.name,
                transaction.date,
                account.transactions.index(transaction),
                userdetails.accounts.index(account)
            ))
    else:
        for acc in userdetails.accounts:
            for transaction in acc.transactions:
                category = Category.query.filter_by(id=transaction.category_id).first()
                category_name = category.name if category else 'None'
                transactions.append(Transaction(
                    transaction.amount,
                    transaction.description,
                    category_name,
                    acc.name,
                    transaction.date,
                    acc.transactions.index(transaction),
                    userdetails.accounts.index(acc)
                ))
    
    transactions.sort(key = lambda transaction: transaction.date)
    return transactions

def get_reverse_sorted_transactions(userdetails, account=None):
    transactions = get_sorted_transactions(userdetails, account=account)
    return reversed(transactions)

def get_periods(userdetails):
    range = get_relative(userdetails.range)
    periods = []

    for transaction in get_sorted_transactions(userdetails):
        start = userdetails.period_start
        while transaction.date < start:
            start -= range
        period = Period(start, start+range)
        if period not in periods:
            periods.append(period)

    return periods

def update(userdetails):
    # Modify current period if needed
    if date.today() >= userdetails.period_end.date():
        userdetails.period_start = userdetails.period_end
        userdetails.period_end += get_relative(userdetails.range)
        db.session.commit()

    # Update bill next occurences
    for bill in userdetails.bills:
        if bill.start <= userdetails.period_start:
            bill.start += get_relative(userdetails.range)
            db.session.commit()