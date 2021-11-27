from collections import namedtuple
from datetime import date
from dateutil.relativedelta import relativedelta

Transaction = namedtuple('Transaction', [
    'amount',
    'description',
    'account_name',
    'date',
    'transaction_index',
    'account_index'
])

Period = namedtuple('Period', [
    'start',
    'end'
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

def get_sorted_transactions(userdetails):
    transactions = []
    for account in userdetails.accounts:
        for transaction in account.transactions:
            transactions.append(Transaction(
                transaction.amount,
                transaction.description,
                account.name,
                transaction.date,
                account.transactions.index(transaction),
                userdetails.accounts.index(account)
            ))
    
    transactions.sort(key = lambda transaction: transaction[3])
    return transactions

def get_reverse_sorted_transactions(userdetails):
    transactions = get_sorted_transactions(userdetails)
    return transactions

def get_periods(userdetails):
    range = get_relative(userdetails.range)
    print(userdetails.range)
    periods = []

    for transaction in get_sorted_transactions(userdetails):
        start = userdetails.period_start
        while transaction.date < start:
            start -= range
        periods.append(Period(start, start+range))

    return periods