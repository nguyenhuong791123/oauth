# -*- coding: UTF-8 -*-
import re
import locale
import json
from flask_jwt_extended import ( create_access_token )

from .dates import token_expires

LANGUAGE_CODES = [ "en", "ja", "vi" ]
def to_locale(language, to_lower=False):
    p = language.find('-')
    if p >= 0:
        if to_lower:
            return language[:p].lower()+'_'+language[p+1:].lower()
        else:
            # Get correct locale for sr-latn
            if len(language[p+1:]) > 2:
                return language[:p].lower()+'_'+language[p+1].upper()+language[p+2:].lower()
            return language[:p].lower()+'_'+language[p+1:].upper()
    else:
        return language.lower()

def parse_accept_lang_header(lang_string):
    accept_language_re = re.compile(r'''
            ([A-Za-z]{1,8}(?:-[A-Za-z]{1,8})*|\*)         # "en", "en-au", "x-y-z", "*"
            (?:\s*;\s*q=(0(?:\.\d{,3})?|1(?:.0{,3})?))?   # Optional "q=1.00", "q=0.8"
            (?:\s*,\s*|$)                                 # Multiple accepts per header.
            ''', re.VERBOSE)

    result = []
    pieces = accept_language_re.split(lang_string)
    if pieces[-1]:
        return []
    for i in range(0, len(pieces) - 1, 3):
        first, lang, priority = pieces[i : i + 3]
        if first:
            return []
        priority = priority and float(priority) or 1.0
        result.append((lang, priority))
    result.sort(key=lambda k: k[1], reverse=True)
    return result

def normalize_language(language):
    return locale.locale_alias.get(to_locale(language, True))

def is_language_supported(language, supported_languages=None):
    if supported_languages is None:
        supported_languages = LANGUAGE_CODES
    if not language:
        return None
    normalized = normalize_language(language)
    if not normalized:
        return None
    # Remove the default encoding from locale_alias.
    normalized = normalized.split('.')[0]
    for lang in (normalized, normalized.split('_')[0]):
        if lang.lower() in supported_languages:
            return lang
    return None

def parse_http_accept_language(accept):
    for accept_lang, unused in parse_accept_lang_header(accept):
        if accept_lang == '*':
            break

        normalized = locale.locale_alias.get(to_locale(accept_lang, True))
        if not normalized:
            continue
        # Remove the default encoding from locale_alias.
        normalized = normalized.split('.')[0]

        for lang_code in (accept_lang, accept_lang.split('-')[0]):
            lang_code = lang_code.lower()
            if lang_code in LANGUAGE_CODES:
                return lang_code
    return None

class UserAgent():
    def __init__(self, req):
        self.host = req.host
        self.path = req.path
        self.method = req.method
        self.remote_addr = req.remote_addr
        self.user_agent = req.user_agent
        self.cookies = req.cookies
        self.accept_languages = req.accept_languages
        self.username = self.set_username(req)
        self.auth = self.set_auth(req.authorization)
        self.api_key = self.set_api_key(req.form.get('apikey', None))
        self.api_token = self.set_api_bearer(req.headers.get('authorization', None))

    def set_username(self, req):        
        if req.json is not None:
            return req.json.get('username')
        else:
            return req.form.get('username')

    def set_auth(self, auth):        
        if auth is not None:
            return auth
        else:
            return None

    def set_api_key(self, key):
        if key is not None:
            return key
        else:
            return None

    def set_api_bearer(self, bearer):
        if bearer is not None and bearer[:5] != 'token' and bearer[:6] != 'Bearer':
            return bearer.replace('Bearer ', '')

    # def set_api_token(self, token):
    #     if token is not None:
    #         self.api_token = token

    def set_session_user(self):
        obj = {}
        obj['username'] = self.username
        obj['api_key'] = self.api_key
        obj['api_token'] = self.api_token
        obj['accept_languages'] = str(self.accept_languages)
        return obj

    def to_json(self):
        obj = {}
        obj['username'] = self.username
        obj['auth'] = self.auth
        obj['api_key'] = self.api_key
        obj['api_token'] = self.api_token
        obj['host'] = self.host
        obj['path'] = self.path
        obj['method'] = self.method
        obj['remote_addr'] = self.remote_addr
        obj['user_agent'] = str(self.user_agent)
        obj['cookies'] = self.cookies
        obj['accept_languages'] = str(self.accept_languages)
        return obj