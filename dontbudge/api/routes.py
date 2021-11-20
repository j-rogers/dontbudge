from flask import request, Blueprint
from flask.json import jsonify
from datetime import date, timedelta
from dontbudge.api import models
from dontbudge.database import db
from dontbudge.auth.jwt import token_required

api = Blueprint('api', __name__)

@api.route('/api/account', methods=['GET', 'POST'])
@token_required
def account():
    if request.method == 'GET':
        return jsonify('nothing here')
    elif request.method == 'POST':
        data = request.get_json()
        name = data['name']
        balance = data['balance']
        user = data['user']
        u = models.UserDetails.query.filter_by(name=user).first()
        if u:
            account = models.Account(name, int(balance), u.id)
            db.session.add(account)
        else:
            # Create user
            u = models.UserDetails(user)
            db.session.add(u)
            db.session.commit()

            # Initial period
            start = date.today()
            range_delta = timedelta(days=u.range)
            end = start + range_delta
            period = models.Period(start, end, u.id)
            db.session.add(period)
            db.session.commit()

            # add account
            account = models.Account(name, int(balance), u.id)
            db.session.add(account)
        db.session.commit()  
        d={'user':u.name,'accounts': [], 'periods': []}
        for a in models.Account.query.filter_by(user=u.id).all():
            d['accounts'].append({'name': a.name, 'balance': a.balance})
        for p in models.Period.query.filter_by(user=u.id).all():
            d['periods'].append({'start': p.start, 'end': p.end})
        return jsonify(d)

@api.route('/api/withdraw', methods=['GET', 'POST'])
@token_required
def withdraw(user):
    # View withdrawals
    if request.method == 'GET':
        userdetails = models.UserDetails.query.filter_by(id=user.userdetails_id).first()
        withdrawals = {}
        for period in userdetails.periods:
            transactions = []
            for transaction in period.transactions:
                transactions.append({
                    'date': transaction.date,
                    'description': transaction.description
                })
            withdrawals[period.id] = {
                'start': period.start,
                'end': period.end,
                'transactions': transactions
            }   
        return jsonify(withdrawals)
    elif request.method == 'POST':
        data = request.get_json()
        amount = int(data['amount'])
        #u.balance -= amount
        return jsonify('dummy')
    else:
        return 'invalid method'

@api.route('/api/deposit', methods=['GET', 'POST'])
@token_required
def deposit():
    return 'none'

@api.route('/api/bill', methods=['GET', 'POST'])
@token_required
def bill():
    return 'none'