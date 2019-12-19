# -*- coding: UTF-8 -*-
from sqlalchemy.orm import relationship
from .db import db, ma

class Grant(db.Model):
    __tablename__ = 'oa_grant'
    __table_args__ = { 'extend_existing': True }

    grant_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    client_id = db.Column(db.String(40), db.ForeignKey('oa_client.client_id'), nullable=False)
    client = relationship('Client')
    user_id = db.Column(db.Integer, db.ForeignKey('oa_users.user_id', ondelete='CASCADE'))
    user = relationship('User')

    code = db.Column(db.String(255), index=True, nullable=False)
    redirect_uri = db.Column(db.String(255))
    expires = db.Column(db.DateTime)
    scopes = db.Column(db.Text)

    @property
    def get_user(self):
        return self.user

    @property
    def get_client(self):
        return self.client
    # @property
    # def scopes(self):
    #     if self.scopes:
    #         return self.scopes.split()
    #     return []

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

class GrantSchema(ma.ModelSchema):
    class Meta:
        model = Grant
        fields = ('grant_id', 'client_id', 'user_id', 'code', 'redirect_uri', 'expires', 'scopes')
