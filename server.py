import os
from igc.util import crypto

manual_enter = False
#Initalize cryptography so that secure encryption can happen
if os.path.exists('./key.txt'):
    debug_file = open('./key.txt', 'r')
    key = debug_file.readline()
    debug_file.close()

    if "!~" in key:
        usb_file_path = key.split("~")[1] + "/key.txt"
        if os.path.exists(usb_file_path):
            usb_file = open(usb_file_path, "r")
            crypto.global_password_key = usb_file.readline()
            usb_file.close()
        else:
            print "Insert USB key at " + usb_file_path + ", program will exit"
            exit(-1)
    else:
        crypto.global_password_key = key
else:
    print "Enter key: "
    input_key = raw_input()

    manual_enter = True
    if len(input_key) == 16:
        crypto.global_password_key = input_key
    else:
        print "Key is not 16 characters, program will exit"
        exit(-1)

checksum = ""
if os.path.exists('./_checksum.txt'):
    checksum_file = open('./_checksum.txt', 'r')
    checksum = checksum_file.readline()
    checksum_file.close()

    if checksum != crypto.encrypt(crypto.get_fernet_with_key(crypto.global_password_key), crypto.Fernet2.IV):
        print "Password is incorrect or the checksum is outdated, program will exit"
        exit(-1)

else:
    if manual_enter:
        print "!!! IMPORTANT !!!"
        print "You must record your key and keep it in a safe place, or you may lose data"
        print "!!! IMPORTANT !!!"

        print "Generate a debug file? (Y/N)"
        debug_answer = raw_input()
        if debug_answer == "Y":
            print "Generate redirect to USB key, enter a USB pathname, if generate a standalone key, enter (Y)"
            generation_answer = raw_input()
            f = open('./key.txt', 'w')
            if generation_answer == "Y":
                f.write(crypto.global_password_key)
            else:
                f.write("!~" + generation_answer)
                usb_file = open(generation_answer + "/key.txt", "w")
                usb_file.write(crypto.global_password_key)
                usb_file.close()
            f.close()

    checksum_file = open('./_checksum.txt', 'w')
    checksum_file.write(crypto.encrypt(crypto.get_fernet_with_key(crypto.global_password_key), crypto.Fernet2.IV))
    checksum_file.close()


from igc.util import cache, util
util.setupLog()
from flask import Flask
from flask import send_from_directory
from flask_cors import CORS

from igc.controller.controller_register import register_controllers

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///./sqllite.db"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
register_controllers(app)
cache.initalizeCache()
for x in range(3):
    print "Starting Cache Thread: " + str(x)
    thread = cache.CacheThread()
    thread.start()
thread = cache.CacheSchedulerThread()
thread.start()

@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

app.run(debug=False, port=5000)