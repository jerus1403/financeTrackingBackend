from security.db import ma
from models.user import UserModel

class UserSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = UserModel
        load_instance = True
        # load_only = ("username", "password")
        # dump_only = ("id", "fullname")