# -*- coding: UTF-8 -*-
import uuid
from flask_jwt_extended import ( create_access_token )
# from datetime import datetime, timedelta
import datetime
from flask import g, request, jsonify, render_template
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.contrib.oauth2 import bind_sqlalchemy
from flask_oauthlib.contrib.oauth2 import bind_cache_grant

from ..cm.utils import is_empty, is_exist, random_N_digits
from ..cm.dates import grant_expires, token_expires, get_pattern, datetime_to_str
from .db import db
from .basic import User
from .client import Client
from .grant import Grant, GRANT_TYPES
from .token import Token

def current_user():
    return g.user

def cache_provider(app):
    oauth = OAuth2Provider(app)
    bind_sqlalchemy(oauth, db.session, user=User, token=Token, client=Client)
    app.config.update({ 'OAUTH2_CACHE_TYPE': 'simple' })
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
        grant = Grant(client_id=client_id, code=code['code'], redirect_uri=request.redirect_uri, scopes=' '.join(request.scopes), user_id=g.username, expires=token_expires())
        db.session.add(grant)
        db.session.commit()

    @oauth.tokensetter
    def set_token(token, request, *args, **kwargs):
        tok = Token(**token)
        tok.basic_id = request.user.id
        tok.client_id = request.client.client_id
        db.session.add(tok)
        db.session.commit()

    @oauth.usergetter
    def get_user(username, password, *args, **kwargs):
        return User.query.filter_by(username=username).first()

    return oauth

def add_client(req):
    auth = None
    if request.method == 'POST':
        if request.json is not None:
            auth = request.json
        else:
            auth['username'] = request.form.get('username')
            auth['password'] = request.form.get('password')
            auth['redirect_uris'] = request.form.get('redirect_uris')
            auth['scopes'] = request.form.get('scopes')

    auth['client_id'] = uuid.uuid4().hex
    auth['client_secret'] = random_N_digits(16, False)
    auth['grant_type'] = GRANT_TYPES.BASIC
    auth['code'] = random_N_digits(12, False) #'read'

    try:
        # access_token = create_access_token(identity=auth['username'])
        # expires = datetime.datetime.now() + datetime.timedelta(seconds=3600)

        if is_exist(auth, 'username') == False or is_empty(auth['username']):
            raise ValueError("Username is required!!!")
        if is_exist(auth, 'password') == False or is_empty(auth['password']):
            raise ValueError("Password is required!!!")
        if is_exist(auth, 'redirect_uris') == False or is_empty(auth['redirect_uris']):
            raise ValueError("Redirect_uris is required!!!")
        if is_exist(auth, 'scopes') == False or is_empty(auth['scopes']):
            auth['scopes'] = None

        u = User(username=auth['username'], password=auth['password'])
        u = u.add()

        c = Client(basic_id=u.id, client_id=auth['client_id'], client_secret=auth['client_secret'], _redirect_uris=auth['redirect_uris'])
        c.add()

        expires = grant_expires()
        g = Grant(basic_id=u.id, client_id=c.client_id, code=auth['code'], _scopes=auth['scopes'], expires=expires)
        g.add()

        # t = Token(basic_id=u.id, client_id=c.client_id, code=auth['code'], _scopes=auth['scopes'], expires=expires)
        # t.add()

        pattern = get_pattern(True, True, '-', False)
        result = {
            'client_id': c.client_id
            ,'client_secret': c.client_secret
            ,'grant_type': auth['grant_type']
            ,'code': auth['code']
            ,'expires': datetime_to_str(expires, pattern)
        }
        # result = [ u.get_schemas(None), c.get_schemas(None), g.get_schemas(None), t.get_schemas(None) ]
        # result = [ u.get_schemas(None), c.get_schemas(None), g.get_schemas(None) ]
    except Exception as err:
        result = { 'msg': str(err) }
        db.session.rollback()
    except ValueError as e:
        result = { 'msg': str(e) }
        db.session.rollback()

    return result

def delete_all_client(req):
    Token().delete_all()
    Grant().delete_all()
    Client().delete_all()
    User().delete_all()

# def refresh_token(req):
#     auth = None
#     if request.method == 'POST':
#         if request.json is not None:
#             auth = request.json
#         else:
#             auth['client_id'] = request.form.get('client_id')
#             auth['client_secret'] = request.form.get('client_secret')
#             auth['refresh_token'] = request.form.get('refresh_token')

def create_oauth(app):
    return default_provider(app)

def create_server(app, oauth=None):
    if not oauth or oauth is None:
        oauth = default_provider(app)

    @app.before_request
    def load_current_user():
        user = User.query.get(1)
        g.user = user

    # curl -v -H "Authorization: Bearer YOUR_API_KEY" http://192.168.10.9:8084/authorize
    # curl -v -H "Content-type: application/json" -X POST -d @data/data.json http://192.168.10.9:8084/authorize
    @app.route('/authorize', methods=[ 'POST' ])
    def api_add_client():
        obj = add_client(request)
        return jsonify(obj), 200

    # curl -v -H "Authorization: Bearer {ACCESS_TOKENT}" -X POST http://192.168.10.9:8084/deleteall
    @app.route('/deleteall', methods=[ 'GET', 'POST' ])
    @oauth.require_oauth()
    def api_delete_client():
        # cu = current_user()
        # print(cu.__dict__)
        return jsonify(delete_all_client(request)), 200

    # curl -v -H "Authorization: Bearer {ACCESS_TOKENT}" -X POST http://192.168.10.9:8084/expires
    @app.route('/expires', methods=[ 'GET', 'POST' ])
    @oauth.require_oauth()
    def api_token_expires():
        return jsonify({ 'msg': True }), 200

    # curl -d client_id={ID} -d client_secret={SECRET} -d _redirect_uris={REDIRECT_URI} -d grant_type={GRANT_TYPE} -d code={CODE} http://192.168.10.9:8084/api/token
    @app.route('/token', methods=[ 'POST', 'GET'])
    @oauth.token_handler
    def api_access_token():
        return {}

    @app.route('/refresh', methods=[ 'GET', 'POST' ])
    @oauth.tokensetter
    def api_token_refresh():
        return {}

    # curl -v -H "Authorization: Bearer {ACCESS_TOKENT}" -X POST http://192.168.10.9:8084/revoke
    @app.route('/revoke', methods=[ 'POST' ])
    @oauth.revoke_handler
    def api_token_revoke():
        pass

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify({ 'msg': False }), 401
        # return jsonify(message=req.error_message), 401

    return app