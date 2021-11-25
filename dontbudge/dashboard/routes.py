"""Dashboard routes

Contains the routes for the dashboard.

Author: Josh Rogers (2021)
"""
import datetime
from flask import request, redirect, render_template
from datetime import timedelta, date
from dontbudge.database import db
from dontbudge.dashboard import dashboard, forms
from dontbudge.auth.jwt import token_required
from dontbudge.auth.models import User
from dontbudge.api.models import Account, Transaction, UserDetails, Bill, Period

@dashboard.route('/', methods=['GET', 'POST'])
def index():
    """Index

    Checks if the JWT token cookie is present, if not then redirect to login.
    """
    if not request.cookies.get('token'):
        return redirect('/login')

    return render_index()

@token_required
def render_index(user: User) -> str:
    """Renders index

    The index is rendered in a seperate function to index() so that the @token_required
    decorater can be used for easier authentication. The index contains basic user
    information such as accounts and recent transactions in the current period.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        A rendered index.html template
    """
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    accounts = userdetails.accounts
    period = userdetails.periods[-1]
    
    # Create new period if needed
    if date.today() >= period.end.date():
        start = period.end
        range_delta = timedelta(days=userdetails.range)
        end = start + range_delta
        period = Period(start, end, userdetails.id)
        db.session.add(period)
        db.session.commit()

    return render_template('index.html', accounts=accounts, period_start=period.start, period_end=period.end, logged_in=True)

@dashboard.route('/account/create', methods=['GET', 'POST'])
@token_required
def create_account(user: User) -> str:
    """Create Account

    Renders the page for creating an account. A valid JWT token is required to access
    this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        A rendered account.html page
    """
    new_account_form = forms.NewAccountForm()
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()

    if request.method == 'POST':
        if new_account_form.validate_on_submit():
            name = new_account_form.name.data
            starting_balance = new_account_form.starting_balance.data
            account = Account(name, starting_balance, userdetails.id)
            db.session.add(account)
            db.session.commit()
            return redirect('/')

    return render_template('account.html', new_account_form=new_account_form, logged_in=True)

@dashboard.route('/transaction/create/withdraw', methods=['GET', 'POST'])
@token_required
def create_withdraw(user: User) -> str:
    """Create Withdraw Transaction

    Renders the page for creating a withdrawal transaction as well as processing
    the transaction request. The significant difference between the withdraw and
    deposit transactions is that withdraw takes money from an account, whereas
    deposit adds money to an account. Otherwise, they use the same page and 
    form. A valid JWT token is required to use this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        Rendered transaction.html page
    """
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    withdraw_form = forms.TransactionForm()
    withdraw_form.account.choices = [(account.id, account.name) for account in userdetails.accounts]

    if request.method == 'POST':
        if withdraw_form.validate_on_submit():
            # Get data from the form
            description = withdraw_form.description.data
            account_id = withdraw_form.account.data
            amount = withdraw_form.amount.data
            date = withdraw_form.date.data

            # Create the Transaction and take away the amount from the specified account
            withdrawal = Transaction(account_id, description, date, amount * -1)
            account = Account.query.filter_by(id=account_id).first()
            account.balance -= amount
            db.session.add(withdrawal)
            db.session.commit()

            return redirect('/')

    return render_template('transaction.html', title='Withdraw', transaction_form=withdraw_form, logged_in=True)

@dashboard.route('/transaction/create/deposit', methods=['GET', 'POST'])
@token_required
def create_deposit(user: User) -> str:
    """Create Deposit Transaction

    Renders the page for creating a deposit transaction as well as processing
    the transaction request. See create_withdraw for differences between a 
    withdraw and deposit transaction. A valid JWT token is required to access
    this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        Rendered transaction.html template
    """
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    deposit_form = forms.TransactionForm()
    deposit_form.account.choices = [(account.id, account.name) for account in userdetails.accounts]

    if request.method == 'POST':
        if deposit_form.validate_on_submit():
            # Get data from form
            description = deposit_form.description.data
            account_id = deposit_form.account.data
            amount = deposit_form.amount.data
            date = deposit_form.date.data
            
            # Create Transaction and add amount to the specified account
            deposit = Transaction(account_id, description, date, amount)
            account = Account.query.filter_by(id=account_id).first()
            account.balance += amount
            db.session.add(deposit)
            db.session.commit()

            return redirect('/')

    return render_template('transaction.html', title='Deposit', transaction_form=deposit_form, logged_in=True)

@dashboard.route('/transaction/view')
@token_required
def view_transactions(user):
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    return redirect(f'/transaction/view/{len(userdetails.periods) - 1}')

@dashboard.route('/transaction/view/<period_index>', methods=['GET', 'POST'])
@token_required
def view_transactions_period(user, period_index):
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    period = userdetails.periods[int(period_index)]
    transactions = []
    for account in userdetails.accounts:
        for transaction  in account.transactions:
            if transaction.date >= period.start and transaction.date < period.end:
                transactions.append((
                    transaction.amount,
                    transaction.description,
                    account.name,
                    transaction.date
                ))

    transactions.sort(key = lambda date: date[3])

    periods = []
    for p in userdetails.periods:
        periods.append((
            userdetails.periods.index(p),
            p.start,
            p.end
        ))
    return render_template('transactions.html', periods=periods, transactions=transactions, period_start=period.start, period_end=period.end, logged_in=True)

@dashboard.route('/bill/create', methods=['GET', 'POST'])
@token_required
def create_bill(user: User) -> str:
    """Create Bill
    
    Renders the page for creating a reoccuring bill. A valid JWT token is required
    to access this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        Rendered bill.html template
    """
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    bill_form = forms.BillForm()
    
    if request.method == 'POST':
        if bill_form.validate_on_submit():
            name = bill_form.name.data
            start = bill_form.start.data
            occurence = bill_form.occurence.data
            amount = bill_form.amount.data

            bill = Bill(start, name, occurence, userdetails.id, amount)
            db.session.add(bill)
            db.session.commit()

            return redirect('/')

    return render_template('bill.html', bill_form=bill_form, logged_in=True)

@dashboard.route('/settings', methods=['GET', 'POST'])
@token_required
def settings(user):
    userdetails = UserDetails.query.filter_by(id=user.userdetails_id).first()
    settings_form = forms.SettingsForm()
    settings_form.range.default = userdetails.range

    if request.method == 'POST':
        if settings_form.validate_on_submit():
            range = settings_form.range.data
            period_start = settings_form.period_start.data

            userdetails.range = range
            range_delta = timedelta(days=userdetails.range)
            end = period_start + range_delta
            period = userdetails.periods[-1]
            period.start = period_start
            period.end = end

            db.session.commit()

            return redirect('/')

    return render_template('settings.html', settings_form=settings_form, logged_in=True)