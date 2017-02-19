import random

from flask import request

from igc.util import crypto
from igc.util.studentvue import check_authentication
from igc.util.util import session_scope


user_keys = {}

def controller(app, models, db):

    @app.route("/api/register", methods=['POST'])
    def register():
        User = models["user"]

        json = request.form
        pin = json["pin"]
        studentId = json["studentId"]
        password = json["password"]
        isCorrect = check_authentication(studentId, password)[0]

        if pin.isdigit():
            key, salt = crypto.generate_fernet_key(pin)
            fernet = crypto.get_fernet_with_key(key)
            hash = fernet.encrypt(bytes(password))

            if isCorrect:
                with session_scope(db) as session:
                    exists = session.query(User).filter(User.student_id == studentId).first()
                    if exists:
                        return 'This user already has an account. Do you want to <a href="../index.html">log in?</a>'
                    else:
                        user = User(int(studentId), hash, salt)
                        db.session.add(user)
                        return "OK"
            else:
                return "Invalid Student ID/PIN combination"
        else:
            return "Invalid PIN"

    @app.route("/api/login", methods=['POST'])
    def login():
        User = models["user"]

        json = request.form
        pin = json["pin"]
        studentId = json["studentId"]

        with session_scope(db) as session:
            user = session.query(User).filter(User.student_id == studentId).first()
            if user:
                key = crypto.generate_fernet_key(pin, user.salt)
                fernet = crypto.get_fernet_with_key(key)
                success, password = crypto.login(fernet, user.hash)
                user_keys[int(studentId)] = password

                if success:
                        tokengen = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                        tokengen = studentId + "_" + tokengen
                        user.token = tokengen
                        return "OK;" + tokengen
                return "Username/password combination is incorrect"