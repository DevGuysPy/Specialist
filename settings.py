import os

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

CONFIRM_ACTIVITY_HTML = \
    "Service: {service}<br>Start: {start}<br>End: {end}<br>" \
    "Description: {description}<br>Please confirm: {confirm_url}"

# mail authentication
MAIL_USERNAME = os.environ.get('APP_MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('APP_MAIL_PASSWORD')

# mail accounts
MAIL_DEFAULT_SENDER = 'natyahlyi@gmail.com'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

SECRET_KEY = os.environ.get('SECRET_KEY')
SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

try:
    from local_settings import *
except ImportError:
    pass
