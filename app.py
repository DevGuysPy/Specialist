from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_cache import Cache
from flask_session import Session
from flask_login import LoginManager
from flask.ext.babel import Babel
import boto

import boto.s3


app = Flask(__name__, static_url_path='/static')

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')

app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)

babel = Babel(app)

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
