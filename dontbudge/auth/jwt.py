from flask import request, jsonify
from functools import wraps
import jwt
import dontbudge
from dontbudge.auth.models import User

def token_required(f):
   @wraps(f)
   def decorator(*args, **kwargs):
       token = None
       if 'x-access-tokens' in request.headers:
           token = request.headers['x-access-tokens']

       if not token:
           return jsonify({'message': 'a valid token is missing'})
       try:
           data = jwt.decode(token, dontbudge.SECRET, algorithms=['HS256'])
           user = User.query.filter_by(id=data['id']).first()
       except:
           return jsonify({'message': 'token is invalid'})
 
       return f(user, *args, **kwargs)
   return decorator

def create_token(user):
    token = jwt.encode({'id': user.id, 'username': user.username}, dontbudge.SECRET)
    return token