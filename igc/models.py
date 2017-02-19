from flask_sqlalchemy import SQLAlchemy


def create_sql_alchemy(app):
    db = SQLAlchemy(app)

    class User(db.Model):
        __tablename__ = "user"

        student_id = db.Column(db.Integer, primary_key=True)
        hash = db.Column(db.Text)
        salt = db.Column(db.String(120))
        token = db.Column(db.String(120))

        def __init__(self, student_id, hash, salt, token=None):
            self.student_id = student_id
            self.hash = hash
            self.salt = salt
            self.token = token

    db.create_all()
    return db, User