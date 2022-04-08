from flask import request, redirect
from functools import wraps
import datetime
import jwt
import dontbudge
from dontbudge.auth.models import User

def token_required(f):
    @wraps(f)
    def decorator(*args, **kwargs):
        token = None
        try:
            token = request.cookies.get('token')
        except:
            pass

        if not token:
            return redirect('/login')
        try:
            data = jwt.decode(token, dontbudge.SECRET, algorithms=['HS256'])
            user = User.query.filter_by(id=data['id']).first()
        except:
            return redirect('/login')

        if not user:
            return redirect('/login')
 
        return f(user, *args, **kwargs)
    return decorator

def create_token(user, remember):
    exp = 9999999999 if remember else datetime.now()
    token = jwt.encode({'id': user.id, 'username': user.username, 'exp': exp}, dontbudge.SECRET)
    return token