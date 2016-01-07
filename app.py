from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_cache import Cache
from flask_session import Session


app = Flask(__name__, static_url_path='/static')

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)

mail = Mail()
mail.init_app(app)

app_session = Session()
app.config['SESSION_TYPE'] = 'filesystem'
app_session.init_app(app)
# basedir = os.path.abspath(os.path.dirname(__file__))


@app.after_request
def call_after_request_callbacks(response):
    db.session.commit()
    return response

import main.models
import main.views
