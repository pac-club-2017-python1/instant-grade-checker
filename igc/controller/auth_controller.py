import base64

from cryptography.fernet import Fernet
from flask import request

from igc.util import crypto
from igc.util.studentvue import check_authentication
from igc.util.util import session_scope

def controller(app, models, db):

    @app.route("/api/register", methods=['POST'])
    def register():
        User = models["user"]

        json = request.form
        pin = json["pin"]
        studentId = json["studentId"]
        password = json["password"]
        status = check_authentication(studentId, password)[0]

        if pin.isdigit():
            salt = Fernet.generate_key()[:25]
            pre_key = pin + "_" + salt
            key = base64.urlsafe_b64encode(pre_key)

            fernet = crypto.get_fernet_with_key(key)
            hash = fernet.encrypt(bytes(password))

            if status == "OK":
                with session_scope() as session:
                    exists = session.query(User).filter(User.student_id == studentId).first()
                    if exists:
                        return 'This user already has an account. Do you want to <a href="../index.html">Log in?</a>'
                    else:
                        user = User(int(studentId), hash, salt)
                        db.session.add(user)
                        db.session.commit()
                        return "OK"
            else:
                return "Invalid Student ID/PIN combination"
        else:
            return "Invalid PIN"