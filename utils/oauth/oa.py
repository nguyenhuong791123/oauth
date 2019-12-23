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
        # expires = datetime.utcnow() + timedelta(seconds=100)
        expires = datetime.datetime.now() + datetime.timedelta(seconds=3600)
        grant = Grant(client_id=client_id, code=code['code'], redirect_uri=request.redirect_uri, scopes=' '.join(request.scopes), user_id=g.username, expires=expires)
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
    auth = {}
    auth['username'] = 'huongnv'
    auth['password'] = 'huongnv080'
    auth['client_id'] = uuid.uuid4().hex
    auth['client_secret'] = random_N_digits(10, False)
    auth['redirect_uris'] = ( 'http://192.168.10.9:8084/' )
    auth['grant_type'] = GRANT_TYPES.PASSWORD
    auth['code'] = random_N_digits(16, False) #'read'
    auth['scopes'] = None #( 'http://192.168.10.9:8084/' )

    try:
        access_token = create_access_token(identity=auth['username'])
        expires = datetime.datetime.now() + datetime.timedelta(seconds=100)

        if is_exist(auth, 'redirect_uris') == False or is_empty(auth['redirect_uris']):
            raise ValueError("Redirect_uris is required!!!")

        u = User(username=auth['username'], password=auth['password'])
        u = u.add()

        c = Client(basic_id=u.id, client_id=auth['client_id'], client_secret=auth['client_secret'], _redirect_uris=auth['redirect_uris'])
        c.add()

        g = Grant(basic_id=u.id, client_id=c.client_id, code=auth['code'], _scopes=auth['scopes'], expires=expires)
        g.add()

        # t = Token(basic_id=u.id, client_id=c.client_id, code=auth['code'], _scopes=auth['scopes'], expires=expires)
        # t.add()

        # result = { 'client_id': c.client_id, 'client_secret': c.client_secret, 'token_type': auth['grant_type'], 'code': auth['code'] }
        # result = [ u.get_schemas(None), c.get_schemas(None), g.get_schemas(None), t.get_schemas(None) ]
        result = [ u.get_schemas(None), c.get_schemas(None), g.get_schemas(None) ]
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

def create_oauth(app):
    return default_provider(app)

def create_server(app, oauth=None):
    if not oauth or oauth is None:
        oauth = default_provider(app)

    @app.before_request
    def load_current_user():
        user = User.query.get(1)
        g.user = user

    @app.route('/authorize', methods=[ 'GET', 'POST' ])
    def api_add_client():
        obj = add_client(request)
        return jsonify(obj), 200

    # curl -d client_id=05dc935620974703a865a5aec9de45ac -d client_secret=rPUdY2g2yS -d redirect_uri=http://192.168.10.9:8084/ -d grant_type=authorization_code -d code=12345 http://192.168.10.9:8084/api/token
    # curl -v -H "Authorization: Bearer 9EsIGGZwkFbpRCYAxejqTBDBxkCRmk" -X POST http://192.168.10.9:8084/deleteall
    @app.route('/deleteall', methods=[ 'GET', 'POST' ])
    @oauth.require_oauth()
    def api_delete_client():
        cu = current_user()
        print(cu.__dict__)
        return jsonify(delete_all_client(request)), 200

    @app.route('/expires', methods=[ 'GET', 'POST' ])
    @oauth.require_oauth()
    def api_toke_expires():
        return jsonify({ 'msg': True }), 200

    @app.route('/token', methods=[ 'POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @app.route('/revoke', methods=[ 'POST' ])
    @oauth.revoke_handler
    def revoke_token():
        pass

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify({ 'msg': False }), 401
        # return jsonify(message=req.error_message), 401

    return app