from splinter import Browser
from flask import Flask, request
from flask import send_from_directory

app = Flask(__name__)
flaskBrowser = Flask(__name__)

@app.route("/api/register", methods=['POST'])
def register():
    json = request.json

    pin = json["pin"]
    studentId = json["studentId"]
    password = json["password"]


@app.route("/api/schoolCredentialCheck", methods=["POST"])
def check_login():
    json = request.form
    studentId = json["studentId"]
    password = json["password"]

    with Browser('phantomjs') as browser:
        url = 'https://studentvue.vbcps.com/Login_Student_PXP.aspx?'
        browser.visit(url)

        browser.find_by_id('username').fill(studentId)
        browser.find_by_id('password').fill(password)
        browser.find_by_id('Submit1').click()

        if browser.url == 'https://studentvue.vbcps.com/Home_PXP.aspx':
            return "OK"
    return "Error"

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run()