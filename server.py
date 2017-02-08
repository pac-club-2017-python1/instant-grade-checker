from flask import Flask
from flask import send_from_directory

app = Flask(__name__)


@app.route("/")
def index():
    return app.send_static_file('index.html')

@app.route("/<path:path>")
def send_static(path):
    return send_from_directory('static', path)

if __name__ == '__main__':
    app.run()