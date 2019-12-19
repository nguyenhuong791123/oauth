# -*- coding: UTF-8 -*-
from sqlalchemy import and_
from ..cm.bcrypts import Bcrypt

from .db import db, ma

class User(db.Model):
    __tablename__ = 'oa_users'
    user_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_mail = db.Column(db.String(150), unique=True, index=True, nullable=False)
    user_pass = db.Column(db.String(80), nullable=False)

    # def check_password(self, password):
    #     return True

    def set_hashpw(self):
        if self.user_pass is not None:
            crypt = Bcrypt()
            crypt.set_salt()
            self.user_pass = crypt.get_hashpw(self.user_pass)

    def is_exist(user):
        result = db.session.query(User).filter(User.email==user['email']).frist()
        if result is None:
            return False
        
        crypt = Bcrypt()
        crypt.set_salt()
        # auth = result[0]
        return crypt.get_checkpw(user['user_pass'], result.user_pass)

    def get_schemas(self, list):
        if list is None or len(list) <= 0:
            return UserSchema(many=True).dump([ self ])
        else:
            return UserSchema(many=True).dump(list)

    def add(self):
        db.session.add(self)
        db.session.commit()
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('user_id', 'user_mail', 'user_pass')
        # fields = ('user_id', 'user_mail')