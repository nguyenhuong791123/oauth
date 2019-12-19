#-*- coding: UTF-8 -*-
import bcrypt

class Bcrypt():
    def __init__(self):
        self.rounds = 12
        self.prefix = b'2a'
        self.salt = None

    def set_rounds(self, rounds):
        self.rounds = rounds

    def set_prefix(self, prefix):
        self.rounds = prefix

    def set_salt(self):
        if self.prefix is not None:
            self.salt = bcrypt.gensalt(rounds=self.rounds, prefix=self.prefix)
        else:
            self.salt = bcrypt.gensalt(rounds=self.rounds)

    def get_hashpw(self, password):
        if self.salt is None:
            return None
        pw  = str(bcrypt.hashpw(password.encode('utf8'), self.salt))
        return pw[2:len(pw)-1]

    def get_checkpw(self, password, hashed):
        return bcrypt.checkpw(password.encode('utf8'), hashed.encode('utf8'))
