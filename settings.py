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
MAIL_DEFAULT_SENDER = 'jyvylo5@gmail.com'

try:
    from local_settings import *
except ImportError:
    pass
