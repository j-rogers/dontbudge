from collections import namedtuple
from datetime import date
from dateutil.relativedelta import relativedelta
from dontbudge.database import db
from dontbudge.api.models import Category, Budget

Transaction = namedtuple('Transaction', [
    'amount',
    'description',
    'category',
    'budget',
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

CategoryT = namedtuple('CategoryT', [
    'name',
    'category_index'
])

BudgetT = namedtuple('BudgetT', [
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

def get_sorted_transactions(userdetails, account=None):
    transactions = []
    if account:
        for transaction in account.transactions:
            category = Category.query.filter_by(id=transaction.category_id).first()
            category_name = category.name if category else 'None'
            budget = Budget.query.filter_by(id=transaction.budget_id).first()
            transactions.append(Transaction(
                transaction.amount,
                transaction.description,
                category_name,
                budget,
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
                budget = Budget.query.filter_by(id=transaction.budget_id).first()
                transactions.append(Transaction(
                    transaction.amount,
                    transaction.description,
                    category_name,
                    budget,
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

def get_categories(userdetails):
    categories = [CategoryT(category.name, userdetails.categories.index(category)) for category in userdetails.categories]
    return categories

def get_budgets(userdetails):
    # Get transactions in this period
    transactions = get_sorted_transactions(userdetails)
    period = get_periods(userdetails)[-1]
    period_transactions = []
    for transaction in transactions:
        if period.start <= transaction.date < period.end:
            period_transactions.append(transaction)
    
    # Calculate used amounts for current period
    used = {budget.name: 0 for budget in userdetails.budgets}
    for transaction in transactions:
        if transaction.budget:
            used[transaction.budget.name] -= transaction.amount

    budgets = []
    for budget in userdetails.budgets:
        budgets.append(BudgetT(budget.name, used[budget.name], budget.amount))

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