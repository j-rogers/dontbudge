"""Dashboard routes

Contains the routes for the dashboard.

Author: Josh Rogers (2021)
"""
from flask import request, redirect, render_template
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from werkzeug.wrappers.response import Response
from dontbudge.database import db
from dontbudge.dashboard import dashboard, forms, utility
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
    userdetails = user.userdetails
    accounts = userdetails.accounts
    
    utility.update(userdetails)

    # Check what bills will be due in the current period
    bills = userdetails.bills
    active_bills = []
    for bill in bills:
        if userdetails.period_start <= bill.start < userdetails.period_end:
            active_bills.append(bill)

    return render_template('index.html', accounts=accounts, period_start=userdetails.period_start, period_end=userdetails.period_end, bills=active_bills, logged_in=True)

@dashboard.route('/account/create', methods=['GET', 'POST'])
@token_required
def create_account(user: User) -> str:
    """Create Account

    Renders the page for creating an account. A valid JWT token is required to access
    this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        A rendered create_account.html page
    """
    userdetails = user.userdetails
    new_account_form = forms.NewAccountForm()

    if request.method == 'POST':
        if new_account_form.validate_on_submit():
            name = new_account_form.name.data
            starting_balance = new_account_form.starting_balance.data
            account = Account(name, starting_balance, userdetails.id)
            db.session.add(account)
            db.session.commit()
            return redirect('/')

    return render_template('create_account.html', new_account_form=new_account_form, logged_in=True)

@dashboard.route('/account/view')
@token_required
def view_accounts(user: User) -> str:
    """View accounts summary

    Renders a page that gives a brief summary of all accounts, i.e. their name
    and balance. A valid JWT token is required to access this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        Rendered accounts.html template
    """
    userdetails = user.userdetails
    accounts = userdetails.accounts
    return render_template('accounts.html', accounts=accounts, logged_in=True)

@dashboard.route('/account/view/<account_index>')
@token_required
def view_account(user: User, account_index: int) -> str:
    """Detailed account summary

    Renders a page that gives a detailed view of a specific account, including
    all transactions of that account. A valid JWT token is required to access
    this endpoint.

    Args:
        user: dontbudge.auth.models.User: Authenticated User model
        account_index -> Integer: Index of the account in the UserDetails.accounts list

    Returns:
        Rendered account.html template
    """
    userdetails = user.userdetails
    account = userdetails.accounts[int(account_index)]

    transactions = utility.get_reverse_sorted_transactions(userdetails)

    return render_template('account.html', account=account, transactions=transactions, logged_in=True)

@dashboard.route('/account/view/<account_index>/transaction/<transaction_index>', methods=['GET', 'POST'])
@token_required
def view_transaction(user: User, account_index: int, transaction_index: int) -> str:
    """View a given transaction of an account

    Renders a page for viewing and editing the details of an existing transaction
    for a given account. A valid JWT token is required to access this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model
        account_index -> Integer: Index of the account in the UserDetails.accounts list
        transaction_index -> Integer: Index of the transaction in the Accounts.transactions list

    Returns:
        A rendered create_transaction.html template
    """
    # Get current details
    userdetails = user.userdetails
    account = userdetails.accounts[int(account_index)]
    transaction = account.transactions[int(transaction_index)]
    
    # Create form
    transaction_form = forms.TransactionForm()
    transaction_form.account.choices = [(account.id, account.name) for account in userdetails.accounts]
    transaction_form.bill.choices = [(bill.id, bill.name) for bill in Bill.query.all()]

    # Update transaction details if any changed
    if transaction_form.validate_on_submit():
        if transaction.description != transaction_form.description.data:
            transaction.description = transaction_form.description.data
        if transaction.account_id != transaction_form.account.data:
            transaction.account_id = transaction_form.account.data
            account.balance -= transaction.amount
            new_account = Account.query.filter_by(id=transaction_form.account.data).first()
            new_account.balance += transaction.amount
        if transaction.amount != transaction_form.amount.data:
            account.balance += transaction.amount if transaction_form.type.data == 'withdraw' else transaction.amount * -1
            transaction.amount = transaction_form.amount.data if transaction_form.type.data == 'deposit' else transaction_form.amount.data * -1
            account.balance += transaction.amount
        if transaction.date != transaction_form.date.data:
            transaction.date = transaction_form.date.data
        if transaction.bill_id != transaction_form.bill.data:
            transaction.bill_id = transaction_form.bill.data
            bill = Bill.query.filter_by(id=transaction_form.bill.data).first()
            bill.start = bill.start + utility.get_relative(bill.occurence)

        # Commit the changes
        db.session.commit()

        return redirect('/')

    # Fill in existing details
    transaction_form.description.data = transaction.description
    transaction_form.account.data = account.id
    transaction_form.amount.data = transaction.amount if transaction.amount > 0 else transaction.amount * -1
    transaction_form.date.data = transaction.date
    transaction_form.bill.data = transaction.bill_id
    transaction_form.type.data = 'deposit' if transaction.amount >= 0 else 'withdraw'

    return render_template('create_transaction.html', title='Edit Transaction', transaction_form=transaction_form, logged_in=True)

@dashboard.route('/transaction/create/<type>', methods=['GET', 'POST'])
@token_required
def create_transaction(user: User, type: str) -> str:
    """Create Transaction

    Renders the page for creating a transaction as well as processing
    the transaction request. The significant difference between the withdraw and
    deposit transactions is that withdraw takes money from an account, whereas
    deposit adds money to an account. Otherwise, they use the same page and 
    form. A valid JWT token is required to use this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model
        type -> String: Type of transaction; either deposit or withdraw

    Returns:
        Rendered create_transaction.html page
    """
    if type not in ('withdraw', 'deposit'):
        return redirect('/')

    userdetails = user.userdetails
    transaction_form = forms.TransactionForm()
    transaction_form.account.choices = [(account.id, account.name) for account in userdetails.accounts]
    transaction_form.bill.choices = [(bill.id, bill.name) for bill in Bill.query.all()]
    transaction_form.type.data = 'deposit' if type == 'deposit' else 'withdraw'

    if request.method == 'POST':
        if transaction_form.validate_on_submit():
            # Get data from the form
            description = transaction_form.description.data
            account_id = transaction_form.account.data
            amount = transaction_form.amount.data
            date = transaction_form.date.data
            bill_id = transaction_form.bill.data

            # Create the Transaction and take/add the amount from the specified account
            transaction = None
            if type == 'withdraw':
                transaction = Transaction(account_id, description, date, amount * -1, bill_id)
                account = Account.query.filter_by(id=account_id).first()
                account.balance -= amount
            elif type == 'deposit':
                transaction = Transaction(account_id, description, date, amount, bill_id)
                account = Account.query.filter_by(id=account_id).first()
                account.balance += amount

            # Update next bill occurence since this one has been paid
            if bill_id:
                bill = Bill.query.filter_by(id=bill_id).first()
                bill.start = bill.start + utility.get_relative(bill.occurence)

            db.session.add(transaction)
            db.session.commit()

            return redirect('/')

    return render_template('create_transaction.html', title=type.capitalize(), transaction_form=transaction_form, logged_in=True)

@dashboard.route('/period/view')
@token_required
def view_transactions(user: User) -> Response:
    """View all transactions in the current period

    Redirects the user to the endpoint that renders the current periods transactions.
    A valid JWT token is required to access this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        A redirection to the endpoint containing the current period
    """
    userdetails = user.userdetails
    periods = utility.get_periods(userdetails)
    return redirect(f'/period/view/{len(periods) - 1}')

@dashboard.route('/period/view/<period_index>')
@token_required
def view_period(user: User, period_index: int) -> str:
    """View all transactions in a given period

    Renders a page that displays a list of all transaction within a given period.
    A valid JWT token is required to access this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model
        period_index -> Integer: Index of the period in the UserDetails.periods list

    Returns:
        Rendered period.html template
    """
    userdetails = user.userdetails
    periods = utility.get_periods(userdetails)
    period = periods[int(period_index)]
    transactions = utility.get_sorted_transactions(userdetails)

    # Get transactions in this period
    period_transactions = []
    for transaction in transactions:
        if period.start <= transaction.date < period.end:
            period_transactions.append(transaction)

    period_transactions.sort(key = lambda transaction: transaction.date)

    return render_template('period.html', periods=periods, transactions=reversed(period_transactions), period_start=period.start, period_end=period.end, logged_in=True)

@dashboard.route('/bill/create', methods=['GET', 'POST'])
@token_required
def create_bill(user: User) -> str:
    """Create Bill
    
    Renders the page for creating a reoccuring bill. A valid JWT token is required
    to access this endpoint.

    Args:
        user -> dontbudge.auth.models.User: Authenticated User model

    Returns:
        Rendered create_bill.html template
    """
    userdetails = user.userdetails
    bill_form = forms.BillForm()
    
    if bill_form.validate_on_submit():
        name = bill_form.name.data
        occurence = bill_form.occurence.data
        start = bill_form.start.data
        amount = bill_form.amount.data

        bill = Bill(start, name, occurence, userdetails.id, amount)
        db.session.add(bill)
        db.session.commit()

        return redirect('/')

    return render_template('create_bill.html', title='Create Bill', bill_form=bill_form, logged_in=True)

@dashboard.route('/bill/view')
@token_required
def view_bills(user):
    userdetails = user.userdetails

    switch = {
        '1W': 'Weekly',
        '2W': 'Fortnightly',
        '1M': 'Monthly',
        '1Q': 'Quartely',
        '1Y': 'Anually'
    }

    bills = []
    for bill in userdetails.bills:
        bills.append(utility.Bill(
            bill.name,
            bill.amount,
            bill.start,
            switch[bill.occurence],
            userdetails.bills.index(bill)
        ))

    return render_template('bills.html', bills=bills, logged_in=True)

@dashboard.route('/bill/edit/<bill_index>', methods=['GET', 'POST'])
@token_required
def edit_bill(user, bill_index):
    userdetails = user.userdetails
    bill = userdetails.bills[int(bill_index)]
    bill_form = forms.BillForm()

    if bill_form.validate_on_submit():
        if bill.name != bill_form.name.data:
            bill.name = bill_form.name.data

        if bill.start != bill_form.start.data:
            bill.start = bill_form.start.data

        if bill.occurence != bill_form.occurence.data:
            bill.occurence = bill_form.occurence.data

        if bill.amount != bill_form.amount.data:
            bill.amount = bill_form.amount.data

        db.session.commit()

        return redirect('/')

    bill_form.name.data = bill.name
    bill_form.start.data = bill.start
    bill_form.occurence.data = bill.occurence
    bill_form.amount.data = bill.amount
    return render_template('create_bill.html', title='Edit Bill', bill_form=bill_form, logged_in=True)

@dashboard.route('/settings', methods=['GET', 'POST'])
@token_required
def settings(user):
    userdetails = user.userdetails
    settings_form = forms.SettingsForm()
    
    if settings_form.validate_on_submit():
        range = settings_form.range.data
        period_start = settings_form.period_start.data

        # Change if there is a difference
        if userdetails.period_start != period_start:
            userdetails.period_start = period_start
            userdetails.period_end = userdetails.period_start + utility.get_relative(userdetails.range)
            db.session.commit()

        if userdetails.range != range:
            userdetails.range = range
            userdetails.period_end = userdetails.period_start + utility.get_relative(range)
            db.session.commit()

        return redirect('/')

    # Fill in defaults
    settings_form.range.data = userdetails.range
    settings_form.period_start.data = userdetails.period_start

    return render_template('settings.html', settings_form=settings_form, logged_in=True)