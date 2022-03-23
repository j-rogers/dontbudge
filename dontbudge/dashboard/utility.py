from collections import namedtuple
from datetime import date
from dateutil.relativedelta import relativedelta
from dontbudge.database import db
from dontbudge.api.models import Transaction

Period = namedtuple('Period', [
    'start',
    'end'
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

def get_transactions(userdetails):
    """Get all transactions of a user
    
    Retrieves all transactions of the given user and returns a sorted list. The
    transactions are in a named tuple Transaction, ready for use in templates.

    Args:
        userdetails -> dontbudge.api.models.UserDetails: User to get transactions of
    
    Returns:
        Sorted list of all dontbudge.dashboard.utility.Transaction's of the user
    """
    transactions = []
    for transaction in userdetails.transactions:
        transactions.append(transaction)
    
    transactions.sort(key = lambda transaction: transaction.date)
    return transactions

def get_account_transactions(account):
    """Get all sorted transactions of an account"""
    transactions = []
    for transaction in account.transactions:
        transactions.append(transaction)

    transactions.sort(key = lambda transaction: transaction.date)
    return transactions

def get_periods(userdetails):
    range = get_relative(userdetails.range)
    periods = []

    for transaction in get_transactions(userdetails):
        start = userdetails.period_start
        while transaction.date < start:
            start -= range
        period = Period(start, start+range)
        if period not in periods:
            periods.append(period)

    return periods

def get_budgets(userdetails):
    # Get current period
    periods = get_periods(userdetails)
    budgets = []
    if not periods:
        for budget in userdetails.budgets:
            budgets.append((budget, 0))
    else:
        period = periods[-1]

        # Calculate used amounts for current period
        for budget in userdetails.budgets:
            used = 0
            for transaction in budget.transactions:
                if period.start <= transaction.date < period.end:
                    used -= transaction.amount

            budgets.append((budget, used))
    
    return budgets

def get_account_balance(account):
    balance = 0
    for transaction in account.transactions:
        balance += transaction.amount

    return balance
