from flask_restful import Resource
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask import request
import traceback

from schemas.income import IncomeSchema
from models.income import IncomeModel

income_list_schema = IncomeSchema(many=True)
income_schema = IncomeSchema()

INCOME_ADDED = 'Income added'
ERROR = 'Something went wrong'

INCOME_NOT_FOUND = 'Income not found'
INCOME_UPDATED = 'Income has been updated'
INCOME_DELETED = 'Income has been deleted'


class CreateIncome(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        income_input = request.get_json()
        income = IncomeModel(income_input['tag'].lower(), income_input['amount'], user_id)
        income_obj = income_schema.dump(income)
        try:
            income.save()
            return {'msg': INCOME_ADDED, 'income': income_obj}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class IncomeResource(Resource):
    @classmethod
    @jwt_required
    def put(cls, income_id):
        income = IncomeModel.find_by_id(income_id)
        income_input = request.get_json()
        # income_obj = income_schema.dump(income)
        if not income:
            return {'msg': INCOME_NOT_FOUND}, 404
        try:
            income.tag = income_input['tag'].lower()
            income.amount = income_input['amount']
            income.save()
            return {'msg': INCOME_UPDATED, 'item': income_input}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500

    @classmethod
    @jwt_required
    def delete(cls, income_id):
        income = IncomeModel.find_by_id(income_id)
        if not income:
            return {'msg': INCOME_NOT_FOUND}, 404
        income.delete()
        return {'msg': INCOME_DELETED}, 200


class IncomeList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        try:
            income_list = income_list_schema.dump(IncomeModel.find_by_user_id(user_id))
            return {'incomes': income_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class IncomeListByTag(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        user_input = request.get_json()['tag']
        search_term = "%{}%".format(user_input)
        try:
            income_list = income_list_schema.dump(IncomeModel.find_by_tag(user_id, search_term))
            return {'incomes': income_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class IncomeListByTimestamp(Resource):
    @classmethod
    @jwt_required
    def get(cls, period):
        user_id = get_jwt_identity()
        # user_input = request.get_json()['period']
        try:
            income_list = income_list_schema.dump(IncomeModel.find_by_timestamp(user_id, period))
            return {'incomes': income_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500





