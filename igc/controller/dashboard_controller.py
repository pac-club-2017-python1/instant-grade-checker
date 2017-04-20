from flask import redirect
from flask import request

from igc.controller import auth_controller
from igc.util import fileio
from igc.util.util import session_scope
from igc.util.cache import students, cacheStudentData

def controller(app, models, db):

    @app.route("/dashboard.html")
    def dashboard():
        User = models["user"]
        token = request.args.get('token')
        with session_scope(db) as session:
            user = session.query(User).filter(User.token == token).first()
            if user and int(user.student_id) in auth_controller.user_keys:
                string = fileio.read("dashboard.html")

                if students[user.student_id]["table_body"] is None:
                    cacheStudentData(user.student_id, students[user.student_id])

                cache = students[user.student_id]
                string = string.replace("{full_name}", cache["full_name"])
                string = string.replace("{table_headers}", cache["welcome_message"])
                string = string.replace("{table_body}", cache["table_body"])
                return string
            else:
                return redirect("index.html?reason=login", code=302)