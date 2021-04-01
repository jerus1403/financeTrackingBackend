from security.db import ma
from models.income import IncomeModel

class IncomeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = IncomeModel
        load_instance = True