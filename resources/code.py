from flask_restful import Resource
from flask import request
from botocore.exceptions import ClientError
import traceback

from models.code import CodeModel
from models.user import UserModel

CODE_NOT_FOUND = 'Code not found'
CODE_EXPIRED = 'Code expired'
CODE_USED = 'Code already used'
CODE_MATCHED = 'Code matched'
CODE_SENT = 'Code has been send to your email'
USER_NOT_FOUND = 'User not found'

class MatchCode(Resource):
    @classmethod
    def post(cls):
        user_input_code = request.get_json()['code']
        code = CodeModel.find_by_code(user_input_code)
        if not code:
            return {'msg' : CODE_NOT_FOUND}, 404
        if code.expired:
            return {'msg': CODE_EXPIRED}, 400
        if code.used:
            return {'msg': CODE_USED}, 400
        code.used = True
        code.save()
        return {'msg': CODE_MATCHED}, 200

class ResendCode(Resource):
    @classmethod
    def post(cls, username):
        user = UserModel.find_user_by_username(username)
        if not user:
            return {'msg': USER_NOT_FOUND}, 404
        try:
            code = user.most_recent_code
            if not code:
                return {'msg': CODE_NOT_FOUND}, 404
            if code:
                code.force_to_expire()
            user.send_code_email()
            return {"msg": CODE_SENT}, 200
        except ClientError as e:
            return e.response['Error']['Message'], 500
        except:
            traceback.print_exc()
            return {"msg": "Failed to resend confirmation email"}, 500
