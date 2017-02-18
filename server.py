from flask.ext.cors import CORS
from splinter import Browser
from flask import Flask, request
from flask import send_from_directory

app = Flask(__name__)
CORS(app)

@app.route("/api/register", methods=['POST'])
def register():
    json = request.form

    pin = json["pin"]
    studentId = json["studentId"]
    password = json["password"]

    return login(studentId, password)[0]


def login(studentId, password):
    with Browser('phantomjs') as browser:
        url = 'https://studentvue.vbcps.com/Login_Student_PXP.aspx'
        browser.visit(url)

        browser.find_by_id('username').fill(studentId)
        browser.find_by_id('password').fill(password)
        browser.find_by_id('Submit1').click()

        if browser.url == 'https://studentvue.vbcps.com/Home_PXP.aspx':
            return "OK", browser
    return "Error", browser

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run()