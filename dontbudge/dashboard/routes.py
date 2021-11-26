"""Dashboard routes

Contains the routes for the dashboard.

Author: Josh Rogers (2021)
"""
from flask import request, redirect, render_template
from datetime import timedelta, date
from dateutil.relativedelta import relativedelta
from werkzeug.wrappers.response import Response
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
    userdetails = user.userdetails
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

    # Check what bills will be due in the current period
    bills = userdetails.bills
    active_bills = []
    for bill in bills:
        if bill.start.date() <= period.start.date():
            switch = {
                '1W': relativedelta(weeks=1),
                '2W': relativedelta(weeks=2),
                '1M': relativedelta(months=1),
                '1Q': relativedelta(months=3),
                '1Y': relativedelta(years=1)
            }
            bill.start += switch[bill.occurence]
            db.session.commit()
        if bill.start.date() >= period.start.date() and bill.start.date() <= period.end.date():
            active_bills.append(bill)

    return render_template('index.html', accounts=accounts, period_start=period.start, period_end=period.end, bills=active_bills, logged_in=True)

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

    transactions = []
    for transaction in account.transactions:
        transactions.append((
            transaction.amount,
            transaction.description,
            account.name,
            transaction.date,
            account.transactions.index(transaction)
        ))

    transactions.sort(key = lambda date: date[3])

    return render_template('account.html', account=account, account_index=account_index, transactions=transactions, logged_in=True)

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

        # Commit the changes
        db.session.commit()

        return redirect('/')

    # Fill in existing details
    transaction_form.description.data = transaction.description
    transaction_form.account.data = account.id
    transaction_form.amount.data = transaction.amount if transaction.amount > 0 else transaction.amount * -1
    transaction_form.date.data = transaction.date
    transaction_form.type.data = 'deposit' if transaction.amount >= 0 else 'withdraw'

    return render_template('create_transaction.html', title='Edit Transaction', transaction_form=transaction_form, logged_in=True)

@dashboard.route('/transaction/create/<type>', methods=['GET', 'POST'])
@token_required
def create_withdraw(user: User, type: str) -> str:
    """Create Withdraw Transaction

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
    transaction_form.type.data = 'deposit' if type == 'deposit' else 'withdraw'

    if request.method == 'POST':
        if transaction_form.validate_on_submit():
            # Get data from the form
            description = transaction_form.description.data
            account_id = transaction_form.account.data
            amount = transaction_form.amount.data
            date = transaction_form.date.data

            # Create the Transaction and take/add the amount from the specified account
            transaction = None
            if type == 'withdraw':
                transaction = Transaction(account_id, description, date, amount * -1)
                account = Account.query.filter_by(id=account_id).first()
                account.balance -= amount
            elif type == 'deposit':
                transaction = Transaction(account_id, description, date, amount)
                account = Account.query.filter_by(id=account_id).first()
                account.balance += amount

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
    return redirect(f'/period/view/{len(userdetails.periods) - 1}')

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
    period = userdetails.periods[int(period_index)]
    transactions = []
    for account in userdetails.accounts:
        for transaction  in account.transactions:
            if transaction.date >= period.start and transaction.date < period.end:
                transactions.append((
                    transaction.amount,
                    transaction.description,
                    account.name,
                    transaction.date,
                    userdetails.accounts.index(account),
                    account.transactions.index(transaction)
                ))

    transactions.sort(key = lambda date: date[3])

    periods = []
    for p in userdetails.periods:
        periods.append((
            userdetails.periods.index(p),
            p.start,
            p.end
        ))
    return render_template('period.html', periods=periods, transactions=transactions, period_start=period.start, period_end=period.end, logged_in=True)

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
    
    if request.method == 'POST':
        if bill_form.validate_on_submit():
            name = bill_form.name.data
            occurence = bill_form.occurence.data
            start = bill_form.start.data
            amount = bill_form.amount.data

            bill = Bill(start, name, occurence, userdetails.id, amount)
            db.session.add(bill)
            db.session.commit()

            return redirect('/')

    return render_template('create_bill.html', bill_form=bill_form, logged_in=True)

@dashboard.route('/settings', methods=['GET', 'POST'])
@token_required
def settings(user):
    userdetails = user.userdetails
    settings_form = forms.SettingsForm()
    settings_form.range.data = userdetails.range

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