from flask import Blueprint, json, request, render_template, flash, jsonify
import hashlib
from dontbudge.auth.forms import RegisterForm, LoginForm
from dontbudge.database import db
from dontbudge.api.models import UserDetails
from dontbudge.auth.models import User
from dontbudge.auth.jwt import create_token

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

            userdetails = UserDetails('New User', 'New User')
            db.session.add(userdetails)
            db.session.commit()

            user = User(userdetails.id, username, password_hash.hexdigest())
            db.session.add(user)
            db.session.commit()
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
                return jsonify({'token': token})
            else:
                return 'failed login'
    return render_template('login.html', form=form)