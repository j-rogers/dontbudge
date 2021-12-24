from collections import namedtuple
from datetime import date
from dateutil.relativedelta import relativedelta
from dontbudge.api.models import UserDetails
from dontbudge.database import db

Account = namedtuple('Account', [
    'name',
    'balance'
])

Transaction = namedtuple('Transaction', [
    'amount',
    'description',
    'category',
    'budget',
    'account_name',
    'date',
    'transaction_index',
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

Category = namedtuple('Category', [
    'name',
    'category_index'
])

Budget = namedtuple('Budget', [
    'name',
    'used',
    'amount'
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

def get_transaction(transaction):
    """Get a single transaction

    Converts a Transaction Model object into a named tuple Transaction object to
    be used in Jinja templates.

    Args:
        transaction: dontbudge.api.models.Transaction: Transaction to be converted
    
    Returns:
        A dontbudge.dashboard.utility.Transaction named tuple
    """
    return Transaction(
            transaction.amount,
            transaction.description,
            transaction.category.name if transaction.category else 'None',
            transaction.budget.name if transaction.budget else 'None',
            transaction.account.name,
            transaction.date,
            transaction.user.transactions.index(transaction)
    )

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
        transactions.append(get_transaction(transaction))
    
    transactions.sort(key = lambda transaction: transaction.date)
    return transactions

def get_account_transactions(account):
    """Get all sorted transactions of an account"""
    transactions = []
    for transaction in account.transactions:
        transactions.append(get_transaction(transaction))

    transactions.sort(key = lambda transaction: transaction.date)
    return Account(account.name, account.balance), reversed(transactions)

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

def get_categories(userdetails):
    categories = [Category(category.name, userdetails.categories.index(category)) for category in userdetails.categories]
    return categories

def get_budgets(userdetails):
    # Get current period
    periods = get_periods(userdetails)
    if not periods:
        return []
    period = periods[-1]

    # Calculate used amounts for current period
    used = {}
    for budget in userdetails.budgets:
        used[budget.name] = 0
        for transaction in budget.transactions:
            if period.start <= transaction.date < period.end:
                used[transaction.budget.name] -= transaction.amount

    budgets = []
    for budget in userdetails.budgets:
        budgets.append(Budget(budget.name, used[budget.name], budget.amount))

    return budgets

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