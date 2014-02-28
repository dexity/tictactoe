
from flask import Flask
from flask.ext.socketio import SocketIO
from redis import Redis, ConnectionError
from .tools import RegexConverter

app = Flask(__name__, static_path="/app/static")
app.config["SECRET_KEY"] = 'some!secret'
app.url_map.converters["regex"] = RegexConverter
app.debug = True
socketio = SocketIO(app)

try:
    red = Redis()
except ConnectionError:
    raise Exception("Please start redis-server: nohup redis-server &")

from . import views

