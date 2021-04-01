from uuid import uuid4
from time import time

from security.db import db

CONFIRMATION_EXPIRATION_TIME = 1800

class ConfirmationModel(db.Model):
    __tablename__ = 'confirmations'
    id = db.Column(db.String, primary_key=True)
    expire_at = db.Column(db.Integer, nullable=False)
    confirmed = db.Column(db.Boolean, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, user_id: int, **kwargs):
        super().__init__(**kwargs)
        self.user_id = user_id
        self.id = uuid4().hex
        self.confirmed = False
        self.expire_at = int(time()) + CONFIRMATION_EXPIRATION_TIME

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id: str) -> "ConfirmationModel":
        return cls.query.filter_by(id=_id).first()

    @property
    def expired(self) -> bool:
        return time() > self.expire_at

    def force_to_expire(self) -> None:
        if not self.expired:
            self.expire_at = int(time())
            self.save()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()


