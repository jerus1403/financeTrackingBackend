from flask import request, url_for
from requests import Response, post
from security.db import db
from security.aws import aws_send_email
import random

from models.confirmation import ConfirmationModel
from models.code import CodeModel

SENDER = "Sender Name <jerus1403@gmail.com>"
RECIPIENT = "{}"
SUBJECT = "Track Money App Confirmation Email"
CHARSET = "UTF-8"
BODY_TEXT = "Please click the link to confirm your registration: {}"
BODY_HTML = """
        <html>
            <head></head>
            <body>
                <h1>Email Confirmation for your Track Money account</h1>
                <p>Please click on this link {} to confirm</p>
            </body>
        </html>
        """

RESET_PW_SUBJECT = "Track Money Reset Password Code"
RESET_PW_BODY_TEXT = "Reset password code: {}"
RESET_PW_BODY_HTML = """
        <html>
            <head></head>
            <body>
                <h1>Reset Password Email</h1>
                <p>Reset password code: {}</p>
            </body>
        </html>
        """


class UserModel(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    fullname = db.Column(db.String, nullable=True)

    confirmation = db.relationship("ConfirmationModel", lazy="dynamic", cascade="all, delete-orphan")
    code = db.relationship("CodeModel", lazy="dynamic", cascade="all, delete-orphan")

    @property
    def most_recent_confirmation(self) -> "ConfirmationModel":
        return self.confirmation.order_by(db.desc(ConfirmationModel.expire_at)).first()

    @property
    def most_recent_code(self) -> "CodeModel":
        return self.code.order_by(db.desc(CodeModel.expire_at)).first()

    def save(self) -> None:
        db.session.add(self)
        db.session.commit()

    def delete(self) -> None:
        db.session.delete(self)
        db.session.commit()

    def send_confirmation_email(self) -> Response:
        confirm_link = request.url_root[0:-1] + url_for("confirmation", confirmation_id=self.most_recent_confirmation.id)
        return aws_send_email(sender=SENDER,
                              recipient=RECIPIENT.format(self.username),
                              charset=CHARSET,
                              subject=SUBJECT,
                              body_html=BODY_HTML.format(confirm_link),
                              body_text=BODY_TEXT.format(confirm_link))

    def send_code_email(self) -> Response:
        code = int(''.join(str(random.randint(0, 9)) for x in range(6)))
        new_code = CodeModel(code, self.id)
        new_code.save()
        return aws_send_email(
            sender=SENDER,
            recipient=RECIPIENT.format(self.username),
            charset=CHARSET,
            subject=RESET_PW_SUBJECT,
            body_html=RESET_PW_BODY_HTML.format(code),
            body_text=RESET_PW_BODY_TEXT.format(code)
        )

    @classmethod
    def find_user_by_username(cls, username: str) -> "UserModel":
        return cls.query.filter_by(username=username).first()

    @classmethod
    def find_user_by_id(cls, _id: int) -> "UserModel":
        return cls.query.filter_by(id=_id).first()
