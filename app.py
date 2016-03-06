import boto

import boto.s3

import logging

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.restless import APIManager
from flask_cache import Cache
from flask_session import Session
from flask_login import LoginManager
from flask.json import JSONEncoder
from flask_socketio import SocketIO
from sqlalchemy_utils import Choice

import jinjahtmlcompress


app = Flask(__name__, static_url_path='/static')

socketio = SocketIO(app)

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.add_extension(jinjahtmlcompress.SelectiveHTMLCompress)
app.jinja_env.add_extension('jinja2.ext.with_')

app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)

logging.basicConfig()
logger = logging.getLogger()
logger.setLevel(logging.INFO)


class CustomJSONEncoder(JSONEncoder):
    def default(self, obj):
        try:
            if isinstance(obj, Choice):
                return {
                    'code': obj.code,
                    'value': obj.value
                }
            iterable = iter(obj)
        except TypeError:
            pass
        else:
            return list(iterable)
        return JSONEncoder.default(self, obj)

app.json_encoder = CustomJSONEncoder

api_manager = APIManager(app, flask_sqlalchemy_db=db)

mail = Mail()
mail.init_app(app)

app_session = Session()
app.config['SESSION_TYPE'] = 'filesystem'
app_session.init_app(app)


conn = boto.connect_s3(app.config['AWS_ACCESS_KEY_ID'],
                       app.config['AWS_SECRET_ACCESS_KEY'],
                       host=app.config['REGION_HOST'])

bucket = conn.get_bucket('spec-bg')

import main.models
import main.views
