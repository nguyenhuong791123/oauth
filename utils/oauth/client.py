# -*- coding: UTF-8 -*-
from sqlalchemy.orm import relationship
from .db import db, ma

class Client(db.Model):
    __tablename__ = 'oa_client'
    __table_args__ = { 'extend_existing': True }

    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True, nullable=False)
    user_id = db.Column(db.ForeignKey('oa_users.user_id'))
    user = relationship('User')

    user_mail = db.Column(db.String(40), nullable=False)
    is_confidential = db.Column(db.Boolean)
    redirect_uris = db.Column(db.Text)
    default_scopes = db.Column(db.Text)
    description = db.Column(db.String(400))

    def __init__(self, **kwargs):
        for k, v in kwargs.items():
            setattr(self, k, v)

    @property
    def get_user(self):
        return self.user

    @property
    def allowed_grant_types(self):
        return [ 'authorization_code', 'password', 'client_credentials', 'refresh_token' ]

    def add(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def get_schemas(self, list):
        if list is None or len(list) <= 0:
            return ClientSchema(many=True).dump([ self ])
        else:
            return ClientSchema(many=True).dump(list)

class ClientSchema(ma.ModelSchema):
    class Meta:
        model = Client
        fields = ('client_id', 'client_secret', 'user_id', 'user_mail', 'is_confidential', 'redirect_uris', 'default_scopes', 'description')
