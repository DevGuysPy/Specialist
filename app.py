# import os

from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy


app = Flask(__name__)
app.debug = True
app.config.from_object('settings')
db = SQLAlchemy(app)
# basedir = os.path.abspath(os.path.dirname(__file__))

import main.models
import main.views
