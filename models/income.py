from security.db import db
from uuid import uuid4
from time import time
from typing import List

NOW = time()
YEAR = 31536000
SIX_MONTH = 15552000
MONTH = 2592000
WEEK = 604800
DAY = 86400
HOUR = 3600
ITEM_PER_PAGE = 15

class IncomeModel(db.Model):
    __tablename__ = 'incomes'
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
    def find_by_id(cls, _id) -> "IncomeModel":
        return cls.query.filter_by(id=_id).first()

    @classmethod
    def find_by_user_id(cls, user_id, page=None) -> List["IncomeModel"]:
        if page:
            return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).paginate(page, per_page=ITEM_PER_PAGE, error_out=False)
        else:
            return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).all()

    @classmethod
    def find_by_timestamp(cls, user_id, period) -> List["IncomeModel"]:
        if period == "hour":
            begin_timestamp = int(NOW) - HOUR
        if period == "day":
            begin_timestamp = int(NOW) - DAY
        if period == "week":
            begin_timestamp = int(NOW) - WEEK
        if period == "month":
            begin_timestamp = int(NOW) - MONTH
        if period == "bi-annual":
            begin_timestamp = int(NOW) - SIX_MONTH
        if period == "year":
            begin_timestamp = int(NOW) - YEAR
        return cls.query.filter_by(user_id=user_id).filter(cls.timestamp.between(begin_timestamp, int(time()))).order_by(cls.timestamp.desc()).all()

    @classmethod
    def find_by_tag(cls, user_id, search_term) -> List["IncomeModel"]:
        return cls.query.filter_by(user_id=user_id).filter(cls.tag.like(search_term)).all()
