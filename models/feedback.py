from security.db import db
from uuid import uuid4
from time import time

class FeedbackModel(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.String, primary_key=True)
    feedback = db.Column(db.String, nullable=True)
    timestamp = db.Column(db.Integer, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    user = db.relationship('UserModel')

    def __init__(self, feedback, user_id, **kwargs):
        super().__init__(**kwargs)
        self.id = uuid4().hex
        self.feedback = feedback
        self.timestamp = int(time())
        self.user_id = user_id

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def find_by_user_id(cls, user_id):
        return cls.query.filter_by(user_id=user_id).order_by(cls.timestamp.desc()).all()


