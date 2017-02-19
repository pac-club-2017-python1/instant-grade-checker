import base64
import os

from cryptography.fernet import Fernet
from flask_cors import CORS
from splinter import Browser
from flask import Flask, request
from flask import send_from_directory
import crypto
import models

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_uri', 'sqlite:///./sqllite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db, User = models.create_sql_alchemy(app)

@app.route("/api/register", methods=['POST'])
def register():
    json = request.form
    pin = json["pin"]
    studentId = json["studentId"]
    password = json["password"]
    status = check_authentication(studentId, password)[0]

    salt = Fernet.generate_key()[:25]
    pre_key = pin + "_" + salt
    key = base64.urlsafe_b64encode(pre_key)

    fernet = crypto.get_fernet_with_key(key)
    hash = fernet.encrypt(bytes(password))

    if status == "OK":
        user = User(studentId, hash, salt)
        db.session.add(user)
        db.session.commit()
        return "OK"
    else:
        return status

def check_authentication(studentId, password):
    with Browser('phantomjs') as browser:
        url = 'https://studentvue.vbcps.com/Login_Student_PXP.aspx'
        browser.visit(url)

        browser.find_by_id('username').fill(studentId)
        browser.find_by_id('password').fill(password)
        browser.find_by_id('Submit1').click()

        if browser.url == 'https://studentvue.vbcps.com/Home_PXP.aspx':
            return "OK", browser
    return "Error", browser

def get_browser_authenticated(studentId, password):
   return check_authentication(studentId, password)[1]

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run()