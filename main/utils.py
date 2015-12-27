from itsdangerous import URLSafeTimedSerializer, BadSignature
from flask.ext.mail import Message
from app import mail, app


def generate_confirmation_token(confirmation_item):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    return serializer.dumps(confirmation_item, salt=app.config['SECURITY_PASSWORD_SALT'])


def confirm_token(token, expiration=3600):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])
    try:
        item = serializer.loads(
            token,
            salt=app.config['SECURITY_PASSWORD_SALT'],
            max_age=expiration
        )
    except BadSignature:
        return
    return item


def send_email(to, subject, template, sender=None):
    msg = Message(
        subject,
        recipients=[to],
        html=template,
        sender=sender or app.config['MAIL_DEFAULT_SENDER']
    )
    mail.send(msg)
