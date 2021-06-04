import os
from flask import Flask, request, jsonify
from flask_restful import Api, Resource
from flask_jwt_extended import JWTManager
from dotenv import load_dotenv
from flask_cors import CORS
from marshmallow import ValidationError
from security.db import db
from flask_migrate import Migrate

from resources import user, confirmation, code, income, expense, feedback
from models import blacklist

load_dotenv()
endpoint = os.environ['RDS_ENDPOINT']
master_user = os.environ['RDS_USERNAME']
master_ps = os.environ['RDS_PASSWORD']
port = os.environ['RDS_PORT']
secret_key = os.environ['SECRET_KEY']
connection_string = 'postgres://{}:{}@{}:{}/postgres'.format(master_user, master_ps, endpoint, port)

application = Flask(__name__)
app = application
CORS(app)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.secret_key = secret_key
db.init_app(app)
migrate = Migrate(app, db, compare_type=True)


class FrontEnd(Resource):
    def get(self):
        return "Happy Budget app version 1.0"


api = Api(app)

jwt = JWTManager(app)


@app.before_first_request
def create_table():
    db.create_all()


@app.errorhandler(ValidationError)
def handle_marshmallow_validation_exception(err):
    return jsonify(err.messages), 400


@jwt.token_in_blacklist_loader
def check_if_token_in_blacklist(decrypted_token):
    jti = decrypted_token['jti']
    return blacklist.Blacklist.is_jti_blacklisted(jti)


api.add_resource(FrontEnd, '/')
# Authentication apis
api.add_resource(user.RegisterUser, '/register')
api.add_resource(user.Login, '/login')
api.add_resource(user.RefreshToken, '/token/refresh')
api.add_resource(user.LogoutAccess, '/logout/access')
api.add_resource(user.LogoutRefresh, '/logout/refresh')
api.add_resource(confirmation.Confirmation, '/confirmation/<string:confirmation_id>')
api.add_resource(confirmation.ConfirmationResend, '/resend_confirmation/<int:user_id>')

# User Resources
api.add_resource(user.UserProfile, '/user')

# Forgot password apis
api.add_resource(user.ForgotPassword, '/forgot-password')
api.add_resource(code.MatchCode, '/match-code')
api.add_resource(code.ResendCode, '/resend-code/<string:username>')
api.add_resource(user.ResetPassword, '/reset-password/<string:username>')

# Income apis
api.add_resource(income.CreateIncome, '/create-income')
api.add_resource(income.IncomeResource, '/income/<string:income_id>')
api.add_resource(income.IncomeList, '/incomes')
api.add_resource(income.IncomeListByPage, '/incomes/items')
api.add_resource(income.IncomeListByTag, '/incomes-by-tag')
api.add_resource(income.IncomeListByTimestamp, '/incomes-by-timestamp/<string:period>')

# Expense apis
api.add_resource(expense.CreateExpense, '/create-expense')
api.add_resource(expense.ExpenseResource, '/expense/<string:expense_id>')
api.add_resource(expense.ExpenseList, '/expenses')
api.add_resource(expense.ExpenseListByPage, '/expenses/items')
api.add_resource(expense.ExpenseListByTag, '/expenses-by-tag')
api.add_resource(expense.ExpenseListByTimestamp, '/expenses-by-timestamp/<string:period>')

# Feedback Resources
api.add_resource(feedback.FeedbackResource, '/create-feedback')
api.add_resource(feedback.FeedbackList, '/feedbacks')

if __name__ == '__main__':
    from security.db import db, ma

    ma.init_app(app)
    app.run(port=8000, debug=True, use_debugger=True)
