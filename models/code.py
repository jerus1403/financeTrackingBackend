from time import time
from uuid import uuid4

from security.db import db

CODE_EXPIRATION_TIME = 1800


class CodeModel(db.Model):
    __tablename__ = 'codes'
    id = db.Column(db.String, primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    code = db.Column(db.Integer, nullable=False)
    used = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, code, user_id, **kwargs):
        super().__init__(**kwargs)
        self.code = code
        self.id = uuid4().hex
        self.used = False
        self.expire_at = int(time()) + CODE_EXPIRATION_TIME
        self.user_id = user_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @property
    def expired(self) -> bool:
        return time() > self.expire_at

    @classmethod
    def find_by_code(cls, code) -> "CodeModel":
        return cls.query.filter_by(code=code).first()

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save()

    def delete(self):
        db.session.delete(self)
        db.session.commit()