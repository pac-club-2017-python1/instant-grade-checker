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