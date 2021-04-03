from flask_restful import Resource
from flask_jwt_extended import jwt_required,get_jwt_identity
from flask import request
import traceback

from schemas.expense import ExpenseSchema
from models.expense import ExpenseModel

expense_list_schema = ExpenseSchema(many=True)
expense_chema = ExpenseSchema()

EXPENSE_ADDED = 'Expense added'
ERROR = 'Something went wrong'

EXPENSE_NOT_FOUND = 'Expense not found'
EXPENSE_UPDATED = 'Expense has been updated'
EXPENSE_DELETED = 'Expense has been deleted'


class CreateExpense(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        expense_input = request.get_json()
        expense = ExpenseModel(expense_input['tag'].lower(), expense_input['amount'], user_id)
        expense_obj = expense_chema.dump(expense)
        try:
            expense.save()
            return {'msg': EXPENSE_ADDED, 'expense': expense_obj}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class ExpenseResource(Resource):
    @classmethod
    @jwt_required
    def put(cls, expense_id):
        expense = ExpenseModel.find_by_id(expense_id)
        expense_input = request.get_json()
        if not expense:
            return {'msg': EXPENSE_NOT_FOUND}, 404
        try:
            expense.tag = expense_input['tag'].lower()
            expense.amount = expense_input['amount']
            expense.save()
            return {'msg': EXPENSE_UPDATED, 'item': expense_input}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500

    @classmethod
    @jwt_required
    def delete(cls, expense_id):
        expense = ExpenseModel.find_by_id(expense_id)
        if not expense:
            return {'msg': EXPENSE_NOT_FOUND}, 404
        expense.delete()
        return {'msg': EXPENSE_DELETED}, 200


class ExpenseList(Resource):
    @classmethod
    @jwt_required
    def get(cls):
        user_id = get_jwt_identity()
        try:
            expense_list = expense_list_schema.dump(ExpenseModel.find_by_user_id(user_id))
            return {'expenses': expense_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class ExpenseListByTag(Resource):
    @classmethod
    @jwt_required
    def post(cls):
        user_id = get_jwt_identity()
        user_input = request.get_json()['tag']
        search_term = "%{}%".format(user_input)
        try:
            expense_list = expense_list_schema.dump(ExpenseModel.find_by_tag(user_id, search_term))
            return {'expenses': expense_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500


class ExpenseListByTimestamp(Resource):
    @classmethod
    @jwt_required
    def get(cls, period):
        user_id = get_jwt_identity()
        # user_input = request.get_json()['period']
        try:
            expense_list = expense_list_schema.dump(ExpenseModel.find_by_timestamp(user_id, period))
            return {'expenses': expense_list}, 200
        except:
            traceback.print_exc()
            return {'msg': ERROR}, 500





