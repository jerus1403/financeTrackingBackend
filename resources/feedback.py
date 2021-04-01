from flask_restful import Resource
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask import request

import traceback

from models.feedback import FeedbackModel
from schemas.feedback import FeedbackSchema

feedback_schema = FeedbackSchema()
feedback_list_schema = FeedbackSchema(many=True)


ERROR = 'Something went wrong'
FEEDBACK_ADDED = 'Feedback submitted'

class FeedbackResource(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        feedback_input = request.get_json()
        feedback = FeedbackModel(feedback_input['feedback'], user_id)
        try:
            feedback.save()
            return {'msg': FEEDBACK_ADDED, 'feedback': feedback_input['feedback']}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class FeedbackList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        try:
            feedback_list = feedback_list_schema.dump(FeedbackModel.find_by_user_id(user_id))
            return {'feedback_list': feedback_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500
