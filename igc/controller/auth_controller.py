import base64
import random

from flask import request, redirect

from igc.util import cache, studentvue
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
        isCorrect, browser = check_authentication(studentId, password)
        if browser is None:
            return "Server connection error"
        studentvue.quit_browser(browser)

        if pin.isdigit():
            try:
                key, salt = crypto.generate_fernet_key(pin)
                fernet = crypto.get_fernet_with_key(key)
                hash = fernet.encrypt(bytes(password))

                if isCorrect:
                    with session_scope(db) as session:
                        exists = session.query(User).filter(User.student_id == studentId).first()
                        if exists:
                            return 'This user already has an account. Do you want to <a href="../index.html">log in?</a>'
                        else:
                            tokengen = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                            tokengen = studentId + "_" + tokengen
                            user = User(int(studentId), hash, salt, token=tokengen)
                            if cache.ALLOW_PIN_CACHE:
                                user.pid = base64.urlsafe_b64encode(pin)
                            session.add(user)
                            session.flush()

                            student = cache.addStudent(int(studentId), password)
                            if student:
                                cache.cacheStudentData(int(studentId), student)
                                response = "OK;" + tokengen
                                user_keys[int(studentId)] = password
                                return response
                            else:
                                return "This user already has an account but database has been desynced. Contact your administrator"
                else:
                    return "Invalid Student ID/PIN combination"
            except ValueError:
                return "Your pin must be 6 digits long"
        else:
            return "Invalid PIN"

    @app.route("/api/updatePassword", methods=['POST'])
    def updatePassword():
        json = request.form
        studentId = json["studentId"]
        password = json["password"]
        pin = json["pin"]

        User = models["user"]
        with session_scope(db) as session:
            user = session.query(User).filter(User.student_id == studentId).first()
            if user:
                key = crypto.generate_fernet_key(pin, user.salt)
                fernet = crypto.get_fernet_with_key(key)
                success, oldPassword = crypto.login(fernet, user.hash)
                if success:
                    isCorrect, browser = studentvue.check_authentication(studentId, password)
                    studentvue.quit_browser(browser)
                    if isCorrect:
                        encryptFernet = crypto.get_fernet_with_key(key)
                        hash = encryptFernet.encrypt(bytes(password))
                        user.hash = hash
                        user.needsUpdate = False

                        cache.addStudent(int(studentId), password, force=True)
                        user_keys[int(studentId)] = password
                        return "OK"
                    else:
                        return "Password is invalid"
                else:
                    return "PIN is invalid"
            else:
                return "User does not exist"

    @app.route("/api/login", methods=['POST'])
    def login():
        User = models["user"]

        json = request.form
        pin = json["pin"]
        studentId = json["studentId"]

        with session_scope(db) as session:
            user = session.query(User).filter(User.student_id == studentId).first()
            if user and len(pin) == 6:
                if user.needsUpdate:
                    return "Change;"
                key = crypto.generate_fernet_key(pin, user.salt)
                fernet = crypto.get_fernet_with_key(key)
                success, password = crypto.login(fernet, user.hash)
                if success:
                    user_keys[int(studentId)] = password
                    if cache.ALLOW_PIN_CACHE:
                        user.pid = base64.urlsafe_b64encode(pin)
                    cache.addStudent(int(studentId), password)
                    tokengen = ''.join(random.choice('0123456789ABCDEF') for i in range(16))
                    tokengen = studentId + "_" + tokengen
                    user.times = user.times + 1
                    user.token = tokengen
                    return "OK;" + tokengen

        return "Username/password combination is incorrect"