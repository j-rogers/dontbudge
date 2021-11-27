from flask import Blueprint, request, render_template, flash, redirect
from datetime import date
import hashlib
from flask.helpers import make_response
from dontbudge.auth.forms import RegisterForm, LoginForm
from dontbudge.database import db
from dontbudge.api.models import UserDetails, Period
from dontbudge.auth.models import User
from dateutil.relativedelta import relativedelta
from dontbudge.auth.jwt import create_token, token_required

auth = Blueprint('auth', __name__, template_folder='templates')

@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            flash('valid') #need to add flashed messages to template
            username = form.username.data
            password = form.password.data
            password_hash = hashlib.md5(password.encode())

            user = User(username, password_hash.hexdigest())
            db.session.add(user)
            db.session.commit()

            start = date.today()
            range_delta = relativedelta(weeks=2)
            end = start + range_delta
            userdetails = UserDetails(username, user.id, '2W', start, end)
            db.session.add(userdetails)
            db.session.commit()

            return redirect('/login')
        else:
            flash('form not valid')
            return 'not gucci'
    return render_template('register.html', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data
            password_hash = hashlib.md5(password.encode())

            user = User.query.filter_by(username=username).first()
            if password_hash.hexdigest() == user.password:
                token = create_token(user)
                response = make_response(redirect('/'))
                response.set_cookie('token', token)
                return response
            else:
                return 'failed login'
    return render_template('login.html', form=form)

@auth.route('/logout')
@token_required
def logout(user):
    response = make_response(redirect('/login'))
    response.delete_cookie('token')
    return response