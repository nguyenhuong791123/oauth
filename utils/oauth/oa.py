# -*- coding: UTF-8 -*-
import uuid
from flask_jwt_extended import ( create_access_token )
from datetime import datetime, timedelta
from flask import g, jsonify, render_template
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.contrib.oauth2 import bind_sqlalchemy
from flask_oauthlib.contrib.oauth2 import bind_cache_grant

from .db import db
from .user import User
from .client import Client
from .grant import Grant
from .token import Token, TOKEN_TYPE

def current_user():
    return g.user

def cache_provider(app):
    oauth = OAuth2Provider(app)
    bind_sqlalchemy(oauth, db.session, user=User, token=Token, client=Client)
    app.config.update({'OAUTH2_CACHE_TYPE': 'simple'})
    bind_cache_grant(app, oauth, current_user)
    return oauth

def sqlalchemy_provider(app):
    oauth = OAuth2Provider(app)
    bind_sqlalchemy(oauth, db.session, user=User, token=Token, client=Client, grant=Grant, current_user=current_user)
    return oauth


def default_provider(app):
    oauth = OAuth2Provider(app)

    @oauth.clientgetter
    def get_client(client_id):
        return Client.query.filter_by(client_id=client_id).first()

    @oauth.grantgetter
    def get_grant(client_id, code):
        return Grant.query.filter_by(client_id=client_id, code=code).first()

    @oauth.tokengetter
    def get_token(access_token=None, refresh_token=None):
        if access_token:
            return Token.query.filter_by(access_token=access_token).first()
        if refresh_token:
            return Token.query.filter_by(refresh_token=refresh_token).first()
        return None

    @oauth.grantsetter
    def set_grant(client_id, code, request, *args, **kwargs):
        expires = datetime.utcnow() + timedelta(seconds=100)
        grant = Grant(client_id=client_id, code=code['code'], redirect_uri=request.redirect_uri, scopes=' '.join(request.scopes), user_id=g.user.id, expires=expires)
        db.session.add(grant)
        db.session.commit()

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        # In real project, a token is unique bound to user and client.
        # Which means, you don't need to create a token every time.
        tok = Token(**token)
        tok.user_id = request.user.user_id
        tok.client_id = request.client.client_id
        db.session.add(tok)
        db.session.commit()

    @oauth.usergetter
    def get_user(user_mail, password, *args, **kwargs):
        # This is optional, if you don't need password credential
        # there is no need to implement this method
        return User.query.filter_by(user_mail=user_mail).first()

    return oauth

def add_client(req):
    auth = {}
    auth['user_mail'] = 'test4@vnext.jp'
    auth['user_pass'] = 'test080'
    auth['client_id'] = uuid.uuid4().hex
    auth['client_secret'] = 'huongnv080'
    auth['redirect_uris'] = 'http://localhost:8004/authorized'
    auth['code'] = '12345'
    auth['scopes'] = 'test3@porters.jp'
    auth['token_type'] = TOKEN_TYPE.BEARER
    access_token = create_access_token(identity=auth['user_mail'])
    expires = datetime.utcnow() + timedelta(seconds=3600)

    # result = None
    try:
        u = User(user_mail=auth['user_mail'], user_pass=auth['user_pass'])
        u.set_hashpw()
        u.add()

        c = Client(user_id=u.user_id, user_mail=auth['user_mail'], client_id=auth['client_id'], client_secret=auth['client_secret'], redirect_uris=auth['redirect_uris'])
        c.add()

        g = Grant(user_id=u.user_id, client_id=c.client_id, code=auth['code'], scopes=auth['scopes'], expires=expires)
        g.add()

        t = Token(user_id=u.user_id, client_id=c.client_id, token_type=auth['token_type'], access_token=access_token, expires_in=0)
        t.add()

        result = [ u.get_schemas(None), c.get_schemas(None), g.get_schemas(None), t.get_schemas(None) ]
    except Exception as err:
        print(err)
        if u is not None:
            u.delete()
        if c is not None:
            c.delete()
        if g is not None:
            g.delete()
        if t is not None:
            t.delete()

    return result

# def prepare_app(app):
#     db.init_app(app)
#     db.app = app
#     db.create_all()

#     client1 = Client(
#         user_mail='dev', client_id='dev', client_secret='dev',
#         redirect_uris=('http://localhost:8000/authorized ' 'http://localhost/authorized'),
#     )

#     client2 = Client(
#         user_mail='confidential', client_id='confidential',
#         client_secret='confidential', client_type='confidential',
#         redirect_uris=(
#             'http://localhost:8000/authorized '
#             'http://localhost/authorized'
#         ),
#     )

#     user = User(user_mail='huongnv@porters.jp')
#     temp_grant = Grant(user_id=1, client_id='confidential', code='12345', scopes='huongnv@porters.jp', expires=datetime.utcnow() + timedelta(seconds=100))
#     access_token = Token(user_id=1, client_id='dev', access_token='expired', expires_in=0)
#     access_token2 = Token(user_id=1, client_id='dev', access_token='never_expire')

#     try:
#         db.session.add(client1)
#         db.session.add(client2)
#         db.session.add(user)
#         db.session.add(temp_grant)
#         db.session.add(access_token)
#         db.session.add(access_token2)
#         db.session.commit()
#     except:
#         db.session.rollback()
#     return app

def create_server(app, oauth=None):
    if not oauth or oauth is None:
        oauth = default_provider(app)
    # print(oauth)
    # app = prepare_app(app)

    @app.before_request
    def load_current_user():
        user = User.query.get(1)
        g.user = user

    @app.route('/home')
    def home():
        return render_template('home.html')

    @app.route('/oauth/authorize', methods=['GET', 'POST'])
    @oauth.authorize_handler
    def authorize(*args, **kwargs):
        # NOTICE: for real project, you need to require login
        if request.method == 'GET':
            # render a page for user to confirm the authorization
            return render_template('confirm.html')

        if request.method == 'HEAD':
            # if HEAD is supported properly, request parameters like
            # client_id should be validated the same way as for 'GET'
            response = make_response('', 200)
            response.headers['X-Client-ID'] = kwargs.get('client_id')
            return response

        confirm = request.form.get('confirm', 'no')
        return confirm == 'yes'

    @app.route('/oauth/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @app.route('/oauth/revoke', methods=['POST'])
    @oauth.revoke_handler
    def revoke_token():
        pass

    @app.route('/api/email')
    @oauth.require_oauth('email')
    def email_api():
        oauth = request.oauth
        return jsonify(email='me@oauth.net', user_mail=oauth.user.user_mail)

    @app.route('/api/client')
    @oauth.require_oauth()
    def client_api():
        oauth = request.oauth
        return jsonify(client=oauth.client.name)

    @app.route('/api/address/<city>')
    @oauth.require_oauth('address')
    def address_api(city):
        oauth = request.oauth
        return jsonify(address=city, user_mail=oauth.user.user_mail)

    @app.route('/api/method', methods=['GET', 'POST', 'PUT', 'DELETE'])
    @oauth.require_oauth()
    def method_api():
        return jsonify(method=request.method)

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify(message=req.error_message), 401

    return app