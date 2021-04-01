import bcrypt
from flask_restful import Resource
from flask import request, redirect
from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_refresh_token_required,
    get_jwt_identity,
    jwt_required,
    get_raw_jwt
)
from botocore.exceptions import ClientError
import traceback
import pdb

from  models.confirmation import ConfirmationModel
from models.user import UserModel
from models.blacklist import Blacklist
from security import security
from schemas.user import UserSchema

user_schema = UserSchema()


class RegisterUser(Resource):
    def post(self):
        user_input = user_schema.load(request.get_json())
        existing_user = UserModel.find_user_by_username(user_input.username)
        if existing_user:
            return {"msg": "Username already exists. Try another one."}, 400
        else:
            try:
                hashed_ps = security.hash_password(user_input.password)
                new_user = UserModel(username=user_input.username, password=hashed_ps)
                new_user.save()
                confirmation = ConfirmationModel(new_user.id)
                confirmation.save()
                new_user.send_confirmation_email()
                return {"success": "User created successfully."}, 200
            except ClientError as e:
                new_user.delete()
                return e.response['Error']['Message'], 500
            except:
                traceback.print_exc()
                new_user.delete()
                return {"msg": "Failed to create user"}, 500


class Login(Resource):
    def post(self):
        user_input = user_schema.load(request.get_json())
        existing_user = UserModel.find_user_by_username(user_input.username)
        if existing_user:
            encoded_input_pw = user_input.password.encode('utf-8')
            encoded_hash_from_db = existing_user.password.encode('utf-8')
            is_password_matched = bcrypt.checkpw(encoded_input_pw, encoded_hash_from_db)
            if is_password_matched:
                confirmation = existing_user.most_recent_confirmation
                if confirmation and confirmation.confirmed:
                    access_token = create_access_token(identity=existing_user.id, fresh=True, expires_delta=False)
                    refresh_token = create_refresh_token(identity=existing_user.id)
                    custom_response = {
                        'access_token': access_token,
                        'refresh_token': refresh_token,
                        'user_id': existing_user.id,
                        'username': existing_user.username
                    }
                    return custom_response, 200
                return {'msg': 'User is not confirmed yet. Please check your email for confirmation.'}, 400
            else:
                return {'msg': 'Invalid password. Try again'}, 400
        else:
            return {'msg': 'User not found.'}, 401


class RefreshToken(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user_id = get_jwt_identity()
        new_access_token = create_access_token(identity=current_user_id, fresh=False)
        return {
                   'access_token': new_access_token
               }, 200


class LogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = Blacklist(jti=jti)
            revoked_token.add()
            return {
                       'msg': 'Assess token has been successfully revoked'
                   }, 200
        except:
            return {
                       'msg': 'Something went wrong'
                   }, 500


class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            revoked_token = Blacklist(jti=jti)
            revoked_token.add()
            pdb.set_trace()
            return {
                       'msg': 'Refresh token has been successfully revoked'
                   }, 200
        except:
            return {
                       'msg': 'Something went wrong'
                   }, 500


class ForgotPassword(Resource):
    def post(self):
        user_email = request.get_json()['email']
        user = UserModel.find_user_by_username(user_email)
        if user:
            user.send_code_email()
            try:
                return {'msg': 'A reset password email has been sent'}, 200
            except ClientError as error:
                return {'msg': error.response['Error']['Message']}, 500
        else:
            return {
                       'msg': 'User does not exist. Please register.'
                   }, 500


class ResetPassword(Resource):
    def post(self, username):
        new_pw = request.get_json()['password']
        hashed_ps = security.hash_password(new_pw)
        user = UserModel.find_user_by_username(username)
        if user:
            user.password = hashed_ps
            user.save()
            return {'msg': 'Password has been reset'}, 200
        else:
            return {'msg': 'Cannot reset password for this user'}, 500


class UserProfile(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        user_input_name = request.get_json()['fullname']
        user = UserModel.find_user_by_id(user_id)
        try:
            user.fullname = user_input_name
            user.save()
            return {'fullname': user_input_name}, 200
        except:
            traceback.print_exc()
            return {'msg': 'Something went wrong'}, 500


    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        user = UserModel.find_user_by_id(user_id)
        if user:
            if not user.fullname:
                return {'msg': 'This user does not have a full name yet'}, 400
            else:
                return {'fullname': user.fullname}, 200
        else:
            return {'msg': 'User not found'}, 401


