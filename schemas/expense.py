from security.db import ma
from models.expense import ExpenseModel


class ExpenseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ExpenseModel
        load_instance = True