# import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
from sqlalchemy.orm import scoped_session
from flask.ext.mail import Mail

app = Flask(__name__, static_url_path='/static')
app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)

session_engine = scoped_session(db.session)
session = session_engine()

mail = Mail()
mail.init_app(app)
# basedir = os.path.abspath(os.path.dirname(__file__))


@app.after_request
def call_after_request_callbacks(response):
    session.commit()
    return response

import main.models
import main.views
