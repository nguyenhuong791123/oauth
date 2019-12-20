# -*- coding: UTF-8 -*-
from sqlalchemy.orm import relationship
from .db import db, ma

class Grant(db.Model):
    __tablename__ = 'oa_grant'
    __table_args__ = { 'extend_existing': True }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    basic_id = db.Column(db.Integer, db.ForeignKey('oa_basic.id', ondelete='CASCADE'))
    user = relationship('User')
    client_id = db.Column(db.String(40), db.ForeignKey('oa_client.client_id'), nullable=False)
    client = relationship('Client')

    code = db.Column(db.String(255), index=True, nullable=False)
    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)
    _scopes = db.Column(db.Text)

    @property
    def get_client(self):
        return self.client

    @property
    def scopes(self):
        if self._scopes:
            return self._scopes.split()

    def get_schemas(self, list):
        if list is None or len(list) <= 0:
            return GrantSchema(many=True).dump([ self ])
        else:
            return GrantSchema(many=True).dump(list)

    def add(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def delete_all(self):
        gs = db.session.query(Grant).all()
        if gs is None:
            return
        for g in gs:
            db.session.delete(g)
            db.session.commit()

class GrantSchema(ma.ModelSchema):
    class Meta:
        model = Grant
        fields = ('id', 'client_id', 'basic_id', 'code', 'redirect_uri', 'expires', '_scopes')

class GRANT_TYPES():
    BASIC = 'authorization_code'
    PASSWORD = 'password'
    BEARER = 'client_credentials'
    REFRESH = 'refresh_token'