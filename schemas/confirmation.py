from security.db import ma
from models.confirmation import ConfirmationModel


class ConfirmationSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = ConfirmationModel
        load_instance = True