from flask_sqlalchemy import SQLAlchemy


def create_sql_alchemy(app):
    db = SQLAlchemy(app)

    class User(db.Model):
        __tablename__ = "user"

        student_id = db.Column(db.Integer, primary_key=True)
        hash = db.Column(CoerceUTF8)
        salt = db.Column(db.String(120))
        token = db.Column(db.String(120))
        fid = db.Column(db.Integer)
        pid = db.Column(db.String(120))
        times = db.Column(db.Integer)
        allowFingerprint = db.Column(db.Boolean)
        needsUpdate = db.Column(db.Boolean)

        def __init__(self, student_id, hash, salt, token=None, fid=-100, pid="NULL", times=0, allowFingerprint=False, needsUpdate=False):
            self.student_id = student_id
            self.hash = hash
            self.salt = salt
            self.token = token
            self.fid = fid
            self.pid = pid
            self.times = times
            self.allowFingerprint = allowFingerprint
            self.needsUpdate = needsUpdate

    db.create_all()
    return db, User

from sqlalchemy.types import TypeDecorator, Unicode
class CoerceUTF8(TypeDecorator):
    """Safely coerce Python bytestrings to Unicode
    before passing off to the database."""

    impl = Unicode

    def process_bind_param(self, value, dialect):
        if isinstance(value, str):
            value = value.decode('utf-8')
        return value