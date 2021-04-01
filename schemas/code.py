from security.db import ma
from models.code import CodeModel

class CodeSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = CodeModel
        load_instance = True