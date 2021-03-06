# -*- coding: UTF-8 -*-
import os
import sys
import json
from flask import Flask, g, session, request, jsonify
from flask_jwt_extended import ( JWTManager )
from flask_cors import CORS

from utils.cm.utils import random_N_digits
from utils.cm.dates import get_datetime
from utils.oauth.db import db
from utils.oauth.oa import default_provider, create_oauth, create_server, add_client, delete_all_client

app = Flask(__name__)
app.secret_key = random_N_digits(24, False)
jwt = JWTManager(app)
app.config['JWT_SECRET_KEY'] = 'scapp'
CORS(app, supports_credentials=True)

app.config.from_object('utils.oauth.config.Config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
oauth = create_oauth(app)
print(oauth.__dict__)

@app.after_request
def after_request(response):
    print('After Request !!![' + get_datetime('%Y-%m-%d %H:%M:%S', None) + ']')
    print(response.__dict__)
    return response

@app.before_request
def before_request():
    print('Before Request !!![' + get_datetime('%Y-%m-%d %H:%M:%S', None) + ']')
    print(request.__dict__)

@app.route('/', methods=['POST'])
@oauth.require_oauth()
def index():
    return "API !!!"

if __name__ == "__main__":
    app = create_server(app, oauth)
    app.run(debug=True, host='0.0.0.0', port=8084)
