from security.db import db
from uuid import uuid4
from time import time
from typing import List

YEAR = 31536000
MONTH = 2592000
WEEK = 604800
DAY = 86400
HOUR = 3600

class ExpenseModel(db.Model):
    __tablename__ = 'expenses'
    id = db.Column(db.String, primary_key=True)
    tag = db.Column(db.String, nullable=False)
    amount = db.Column(db.DECIMAL(asdecimal=False), nullable=False)
    timestamp = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, tag, amount, user_id, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.tag = tag
        self.amount = amount
        self.timestamp = int(time())
        self.user_id = user_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    @classmethod
    def find_by_id(cls, _id) -> "ExpenseModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user_id(cls, user_id) -> List["ExpenseModel"]:
        return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).all()

    @classmethod
    def find_by_timestamp(cls, user_id, period) -> List["ExpenseModel"]:
        if period == "hour":
            begin_timestamp = int(time()) - HOUR
        if period == "day":
            begin_timestamp = int(time()) - DAY
        if period == "week":
            begin_timestamp = int(time()) - WEEK
        if period == "month":
            begin_timestamp = int(time()) - MONTH
        if period == "year":
            begin_timestamp = int(time()) - YEAR
        return cls.query.filter_by(user_id=user_id).filter(cls.timestamp.between(begin_timestamp, int(time()))).order_by(cls.timestamp.desc()).all()

    @classmethod
    def find_by_tag(cls, user_id, search_term) -> List["ExpenseModel"]:
        return cls.query.filter_by(user_id=user_id).filter(cls.tag.like(search_term)).all()
