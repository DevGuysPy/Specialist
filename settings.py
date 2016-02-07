# -*- encoding: utf-8 -*-
import os

MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True

# mail authentication
MAIL_USERNAME = os.environ.get('APP_MAIL_USERNAME')
MAIL_PASSWORD = os.environ.get('APP_MAIL_PASSWORD')

# mail accounts
MAIL_DEFAULT_SENDER = 'natyahlyi@gmail.com'

SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

SECRET_KEY = os.environ.get('SECRET_KEY')

SECURITY_PASSWORD_SALT = os.environ.get('SECURITY_PASSWORD_SALT')

RECAPTCHA_OPTIONS = {'theme': 'white'}
RECAPTCHA_PUBLIC_KEY = os.environ.get('RECAPTCHA_PUBLIC_KEY')
RECAPTCHA_PRIVATE_KEY = os.environ.get('RECAPTCHA_PRIVATE_KEY')

BASE_DIR = os.path.dirname(os.path.realpath(__file__))

REGION_HOST = os.environ.get('REGION_HOST')
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')

LANGUAGES = {
    'en': 'English',
    'uk': 'Українська',
    'ru': 'Русский'
}

try:
    from local_settings import *
except ImportError:
    pass
