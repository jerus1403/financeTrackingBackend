from security.db import ma
from models.feedback import FeedbackModel

class FeedbackSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = FeedbackModel
        load_instance = True
