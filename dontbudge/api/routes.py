from flask import request, Blueprint
from datetime import datetime, timedelta
from flask.json import jsonify

api = Blueprint('api', __name__)

class Period:
    def __init__(self):
        self.range = timedelta(days=14)
        self.start_date = datetime(2021, 11, 11)

class Account:
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

class User:
    def __init__(self):
        self.periods = [Period(),]
        self.accounts = []

u = User()

@api.route('/')
def hello():
    return 'Hello world'

@api.route('/api/account', methods=['GET', 'POST'])
def account():
    if request.method == 'GET':
        return jsonify('nothing here')
    elif request.method == 'POST':
        data = request.get_json()
        name = data['name']
        balance = data['balance']
        u.accounts.append(Account(name, balance))
        d={'accounts': []}
        for a in u.accounts:
            d['accounts'].append({'name': a.name, 'balance': a.balance})
        return jsonify(d)

@api.route('/api/withdraw', methods=['GET', 'POST'])
def withdraw():
    # View withdrawals
    if request.method == 'GET':
        return jsonify(f'Viewing withdrawals for period {u.periods[0].start_date.strftime("%Y/%m/%d")}-{(u.periods[0].start_date + u.periods[0].range).strftime("%Y/%m/%d")}')
    elif request.method == 'POST':
        data = request.get_json()
        amount = int(data['amount'])
        u.balance -= amount
        return jsonify(u.balance)
    else:
        return 'invalid method'

if __name__ == '__main__':
    
    app.run(host='0.0.0.0')