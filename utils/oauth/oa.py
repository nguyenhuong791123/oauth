# -*- coding: UTF-8 -*-
import uuid
from flask_jwt_extended import ( create_access_token )
# from datetime import datetime, timedelta
import datetime
from flask import g, request, jsonify, render_template
from flask_oauthlib.provider import OAuth2Provider
from flask_oauthlib.contrib.oauth2 import bind_sqlalchemy
from flask_oauthlib.contrib.oauth2 import bind_cache_grant

from ..cm.utils import random_N_digits
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
        expires = datetime.datetime.now() + datetime.timedelta(seconds=100)
        grant = Grant(client_id=client_id, code=code['code'], redirect_uri=request.redirect_uri, scopes=' '.join(request.scopes), user_id=g.login_id, expires=expires)
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
    def get_user(user_mail, password, *args, **kwargs):
        return User.query.filter_by(login_id=login_id).first()

    return oauth

def add_client(req):
    auth = {}
    auth['login_id'] = 'huongnv'
    auth['password'] = 'huongnv080'
    auth['client_id'] = uuid.uuid4().hex
    auth['client_secret'] = random_N_digits(10, False)
    auth['redirect_uris'] = ( 'http://192.168.10.9:8084/deleteall' )
    auth['token_type'] = GRANT_TYPES.BEARER
    auth['code'] = 'read'
    auth['scopes'] = ( 'http://192.168.10.9:8084/deleteall' )

    try:
        access_token = create_access_token(identity=auth['login_id'])
        expires = datetime.datetime.now() + datetime.timedelta(seconds=100)

        u = User(login_id=auth['login_id'], password=auth['password'])
        u = u.add()

        c = Client(basic_id=u.id, client_id=auth['client_id'], client_secret=auth['client_secret'], _redirect_uris=auth['redirect_uris'])
        c.add()

        g = Grant(basic_id=u.id, client_id=c.client_id, code=auth['code'], _scopes=auth['scopes'], expires=expires)
        g.add()

        result = { 'client_id': c.client_id, 'client_secret': c.client_secret }
        # result = [ u.get_schemas(None), c.get_schemas(None), g.get_schemas(None) ]
    except Exception as err:
        result = { 'msg': str(err) }
        db.session.rollback()

    return result

def delete_all_client(req):
    Token().delete_all()
    Grant().delete_all()
    Client().delete_all()
    User().delete_all()

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
    @app.route('/deleteall', methods=[ 'GET', 'POST' ])
    @oauth.require_oauth()
    def api_delete_client():
        obj = delete_all_client(request)
        return jsonify(obj), 200

    @app.route('/api/token', methods=['POST', 'GET'])
    @oauth.token_handler
    def access_token():
        return {}

    @app.route('/api/revoke', methods=['POST'])
    @oauth.revoke_handler
    def revoke_token():
        pass

    @oauth.invalid_response
    def require_oauth_invalid(req):
        return jsonify(message=req.error_message), 401

    return app