from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.mail import Mail
from flask_cache import Cache
# from flask.ext.login import LoginManager
# from flask.ext.openid import OpenID


app = Flask(__name__, static_url_path='/static')

cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(app)

app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)

mail = Mail()
mail.init_app(app)
# basedir = os.path.abspath(os.path.dirname(__file__))

# lm = LoginManager()
# lm.init_app(app)
# oid = OpenID(app, os.path.join(basedir, 'tmp'))

@app.after_request
def call_after_request_callbacks(response):
    db.session.commit()
    return response

import main.models
import main.views
