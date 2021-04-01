from flask_restful import Resource
from flask import redirect
from botocore.exceptions import ClientError
import traceback

from models.confirmation import ConfirmationModel
from models.user import UserModel

USER_NOT_FOUND = 'User not found'
CONFIRMATION_NOT_FOUND = 'Confirmation not found'
ALREADY_CONFIRMED = 'User already confirmed'
LINK_EXPIRED = 'The link has expired'
SEND_EMAIL_SUCCESSFUL = 'Email has been sent'


class Confirmation(Resource):
    @classmethod
    def get(cls, confirmation_id: str):
        confirmation = ConfirmationModel.find_by_id(confirmation_id)
        if not confirmation:
            return {'msg': CONFIRMATION_NOT_FOUND}, 404
        if confirmation.expired:
            return {'msg': LINK_EXPIRED}, 400
        if confirmation.confirmed:
            return {'msg': ALREADY_CONFIRMED}, 400

        confirmation.confirmed = True
        confirmation.save()
        return redirect("http://127.0.0.1:8000", code=302)


class ConfirmationResend(Resource):
    @classmethod
    def post(cls, user_id: int):
        user = UserModel.find_user_by_id(user_id)
        if not user:
            return {'msg': USER_NOT_FOUND}, 404
        try:
            confirmation = user.most_recent_confirmation
            if not confirmation:
                return {'msg': CONFIRMATION_NOT_FOUND}, 404
            if confirmation:
                if confirmation.confirmed:
                    return {'msg': ALREADY_CONFIRMED}, 400
                confirmation.force_to_expire()
            new_confirmation = ConfirmationModel(user_id)
            new_confirmation.save()
            user.send_confirmation_email()
            return {'msg': SEND_EMAIL_SUCCESSFUL}, 201
        except ClientError as e:
            return e.response['Error']['Message'], 500
        except:
            traceback.print_exc()
            return {"msg": "Failed to resend confirmation email"}, 500


