import os

from flask import Flask
from flask import send_from_directory
from flask_cors import CORS

from igc.controller.controller_register import register_controllers
from igc.util import cache

app = Flask(__name__, static_url_path='/html')
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('database_uri', 'sqlite:///./sqllite.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

register_controllers(app)

@app.route("/")
def index():
    return app.send_static_file('/html/index.html')

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('/html', path)

if __name__ == '__main__':
    thread = cache.CacheThread()
    thread.start()

    app.run(debug=True, port=5000)
    # http_server = WSGIServer(('', 5000), app)
    # http_server.serve_forever()