from flask import redirect
from flask import request

from igc.controller import auth_controller
from igc.util import crypto
from igc.util import fileio
from igc.util import studentvue
from igc.util.util import session_scope


def controller(app, models, db):

    @app.route("/dashboard.html")
    def dashboard():
        User = models["user"]
        token = request.args.get('token')
        with session_scope(db) as session:
            user = session.query(User).filter(User.token == token).first()
            if user and auth_controller.user_keys[user.student_id] is not None:
                string = fileio.read("static/dashboard.html")
                password = auth_controller.user_keys[user.student_id]
                browser = studentvue.get_browser_authenticated(user.student_id, password)
                browser.click_link_by_partial_href('PXP_Gradebook.aspx?AGU=0')
                string = string.replace("{full_name}", browser.find_by_css('.UserHead').find_by_css("*").first.text.title())
                string = string.replace("{table_headers}", browser.find_by_css(".row_subhdr").first.html.replace('<td align="left" valign="top">Resources</td>', ""))

                tableBody = ""

                list = browser.find_by_css(".altrow1,.altrow2")
                for clazz in list:
                    children = clazz.find_by_tag("a")
                    tableBody += "<tr>"
                    for child in children:
                        tableBody += ("<td>" + child.text + "</td>")
                    tableBody += "<tr>"
                string = string.replace("{table_body}", tableBody)
                return string
            else:
                return redirect("index.html?reason=login", code=302)