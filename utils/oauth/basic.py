# -*- coding: UTF-8 -*-
from sqlalchemy import and_
from ..cm.bcrypts import Bcrypt

from .db import db, ma

class User(db.Model):
    __tablename__ = 'oa_basic'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, index=True, nullable=False)
    password = db.Column(db.String(80), nullable=False)

    def set_hashpw(self):
        if self.password is not None:
            crypt = Bcrypt()
            crypt.set_salt()
            self.password = crypt.get_hashpw(self.password)

    def is_exist(self):
        result = db.session.query(User).filter(User.username==self.username).first()
        if result is None:
            return self
        
        crypt = Bcrypt()
        crypt.set_salt()
        isExist = crypt.get_checkpw(self.password, result.password)
        if isExist:
            return result
        return self

    def get_schemas(self, list):
        if list is None or len(list) <= 0:
            return UserSchema(many=True).dump([ self ])
        else:
            return UserSchema(many=True).dump(list)

    def add(self):
        is_self = self.is_exist()
        if is_self.id is not None:
            self = is_self
        else:
            self.set_hashpw()
            db.session.add(self)
            db.session.commit()
        print(self.__dict__)
        return self

    def delete(self):
        db.session.delete(self)
        db.session.commit()
        return self

    def delete_all(self):
        us = db.session.query(User).all()
        if us is None:
            return
        for u in us:
            db.session.delete(u)
            db.session.commit()

class UserSchema(ma.ModelSchema):
    class Meta:
        model = User
        fields = ('id', 'username', 'password')
        # fields = ('id', 'username')