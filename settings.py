MAIL_SERVER = 'smtp.googlemail.com'
MAIL_PORT = 465
MAIL_USE_TLS = False
MAIL_USE_SSL = True
CONFIRM_ACTIVITY_HTML = \
    "Service: {service}<br>Start: {start}<br>End: {end}<br>Please confirm: {confirm_url}"

try:
    from local_settings import *
except ImportError:
    pass
