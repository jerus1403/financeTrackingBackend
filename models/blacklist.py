from security.db import db

class Blacklist(db.Model):
    __tablename__ = "blacklist"

    id = db.Column(db.Integer, primary_key=True)
    jti = db.Column(db.String(120), nullable=False)

    def add(self) -> None:
        db.session.add(self)
        db.session.commit()

    @classmethod
    def is_jti_blacklisted(cls, jti: str) -> "Blacklist":
        query = cls.query.filter_by(jti=jti).first()
        return bool(query)