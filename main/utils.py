import datetime
import random

from flask import abort, url_for, session, redirect, flash, render_template
from flask.ext.mail import Message
from flask.ext.login import login_user, login_required, logout_user

from itsdangerous import URLSafeTimedSerializer, BadSignature

import settings
from app import mail, app, login_manager, db, bucket
from models import User, UserUserActivity


def generate_confirmation_token(confirmation_item):
    serializer = URLSafeTimedSerializer(app.config['SECRET_KEY'])

    return serializer.dumps(confirmation_item,
                            salt=app.config['SECURITY_PASSWORD_SALT'])


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


def get_model_column_values(model, columns):
    """
    Func for receiving values of given columns in given model.
    Sample of columns:
    columns = [
        {
            'dict_key': 'name', # This is a name of dict key for this column
            'column': 'title' # This is a name of model column
        }
    ]

    :param model: model
    :param list columns: columns
    :return:
    """

    data = []
    for obj in model.query.all():
        obj_data = {}
        for column in columns:
            obj_data[column['dict_key']] = getattr(obj, column['column'])
        data.append(obj_data)

    return data


@app.route('/send_verification_email/user/<int:user_id>', methods=['POST'])
def send_user_verification_email(user_id):
    user = User.query.get(int(user_id))
    if not user:
        return abort(404)

    token = generate_confirmation_token(user.id)
    confirm_url = url_for('confirm_user',
                          token=token, _external=True)
    html = render_template("ConfirmUserEmail.html",
                           full_name=user.full_name(),
                           confirm_url=str(confirm_url))
    send_email(to=user.email,
               subject='Please confirm your account',
               template=html)

    return 'ok'


@app.route('/user_user_activity/confirm/<token>')
def confirm_specialist_activity(token):
    activity_id = confirm_token(token)
    activity = UserUserActivity.query.filter_by(
            id=activity_id).first_or_404()

    if activity.confirmed:
        flash('Activity already confirmed.')
    else:
        activity.confirmed = True
        flash('You have confirmed your relationship with {}.'.format(
                activity.to_user.full_name()))

    return redirect(url_for('user_profile', user_id=activity.to_user.id))


@app.route('/user/confirm/<token>')
def confirm_user(token):
    user_id = confirm_token(token)
    user = User.query.filter_by(id=user_id).first_or_404()

    user.confirmed = True
    session['user_first_log_in'] = True

    login_user(user)
    return redirect(url_for('user_profile', user_id=user.id))


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.after_request
def call_after_request_callbacks(response):
    db.session.commit()
    return response


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect('/')


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


def account_not_found():
    return render_template('404.html')


@app.template_filter()
def datetimefilter(value, format='%Y/%m/%d %H:%M'):
    return value.strftime(format)


app.jinja_env.filters['datetime'] = datetimefilter


@app.template_filter()
def datefilter(value, format='%Y/%m/%d'):
    return value.strftime(format)


app.jinja_env.filters['date'] = datefilter


@app.template_filter()
def timefilter(value, format='%H:%M'):
    return value.strftime(format)


app.jinja_env.filters['time'] = timefilter


@app.context_processor
def current_time():
    current_time = datetime.datetime.now()
    return dict(current_time=current_time)


def get_random_background():
    img = random.choice(list(bucket.list()))
    return 'https://' + settings.REGION_HOST + '/spec-bg/' + img.name
