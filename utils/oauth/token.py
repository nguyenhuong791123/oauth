# -*- coding: UTF-8 -*-
from datetime import datetime, timedelta
from sqlalchemy.orm import relationship
from .db import db, ma

class Token(db.Model):
    __tablename__ = 'oa_token'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    basic_id = db.Column(db.Integer, db.ForeignKey('oa_basic.id', ondelete='CASCADE'))
    user = relationship('User')
    client_id = db.Column(db.String(40), db.ForeignKey('oa_client.client_id'), nullable=False)
    client = relationship('Client')

    token_type = db.Column(db.String(40), nullable=False)
    access_token = db.Column(db.String(255), unique=True)
    refresh_token = db.Column(db.String(255), unique=True)
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    def __init__(self, **kwargs):
        expires_in = kwargs.pop('expires_in', None)
        if expires_in is not None:
            self.expires = datetime.utcnow() + timedelta(seconds=expires_in)
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def get_client(self):
        return self.client

    @property
    def scopes(self):
        if self.scopes:
            return self.scopes.split()
        return []

    def add(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def delete_all(self):
        ts = db.session.query(Token).all()
        if ts is None:
            return
        for t in ts:
            db.session.delete(t)
            db.session.commit()

    def get_schemas(self, list):
        if list is None or len(list) <= 0:
            return TokenSchema(many=True).dump([ self ])
        else:
            return TokenSchema(many=True).dump(list)

class TokenSchema(ma.ModelSchema):
    class Meta:
        model = Token
        fields = ('id', 'client_id', 'basic_id', 'token_type', 'access_token', 'refresh_token', 'expires', '_scopes')
