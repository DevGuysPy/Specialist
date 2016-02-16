from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask.ext.restless import APIManager
from flask_cache import Cache
from flask_session import Session
from flask_login import LoginManager
import jinjahtmlcompress


app = Flask(__name__, static_url_path='/static')

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

login_manager = LoginManager()
login_manager.login_view = 'login'
login_manager.init_app(app)

app.jinja_env.add_extension('jinja2.ext.loopcontrols')
app.jinja_env.add_extension(jinjahtmlcompress.SelectiveHTMLCompress)
app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)

api_manager = APIManager(app, flask_sqlalchemy_db=db)

mail = Mail()
mail.init_app(app)

app_session = Session()
app.config['SESSION_TYPE'] = 'filesystem'
app_session.init_app(app)


import main.models
import main.views
