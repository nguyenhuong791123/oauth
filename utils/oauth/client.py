# -*- coding: UTF-8 -*-
from sqlalchemy.orm import relationship
from .db import db, ma

class Client(db.Model):
    __tablename__ = 'oa_client'
    __table_args__ = { 'extend_existing': True }

    client_id = db.Column(db.String(40), primary_key=True)
    client_secret = db.Column(db.String(55), unique=True, index=True, nullable=False)
    basic_id = db.Column(db.Integer, db.ForeignKey('oa_basic.id', ondelete='CASCADE'))
    user = relationship('User')

    is_confidential = db.Column(db.Boolean)
    _redirect_uris = db.Column(db.Text)
    _default_scopes = db.Column(db.Text)
    description = db.Column(db.String(400))

    @property
    def client_type(self):
        if self.is_confidential:
            return 'confidential'
        return 'public'

    @property
    def redirect_uris(self):
        if self._redirect_uris:
            return self._redirect_uris.split()
        return []

    @property
    def default_redirect_uri(self):
        return self.redirect_uris[0]
        return []

    @property
    def default_scopes(self):
        if self._default_scopes:
            return self._default_scopes.split()
        return []

    @property
    def allowed_grant_types(self):
        return [ 'authorization_code', 'password', 'client_credentials', 'refresh_token' ]

    def get_user(self):
        return self.user

    def add(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def delete_all(self):
        cs = db.session.query(Client).all()
        if cs is None:
            return
        for c in cs:
            db.session.delete(c)
            db.session.commit()

    def get_schemas(self, list):
        if list is None or len(list) <= 0:
            return ClientSchema(many=True).dump([ self ])
        else:
            return ClientSchema(many=True).dump(list)

class ClientSchema(ma.ModelSchema):
    class Meta:
        model = Client
        fields = ('client_id', 'client_secret', 'basic_id', 'is_confidential', '_redirect_uris', '_default_scopes', 'description')
