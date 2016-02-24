import datetime
from flask import abort, url_for, session, redirect, flash, render_template, \
    jsonify, request, json
from flask.ext.mail import Message
from flask.ext.login import login_user, login_required, logout_user,\
    current_user

from itsdangerous import URLSafeTimedSerializer, BadSignature

from app import mail, app, login_manager, db
from models import User, UserUserActivity
from forms import ChangePasswordForm, SetPhoneForm, ResetPasswordForm, EmailForm
from settings import client

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


@app.route('/password/confirm/<token>')
def confirm_user_to_reset_password(token):
    user_id = confirm_token(token)
    user = User.query.filter_by(id=user_id).first_or_404()
    if user:
        return redirect(url_for('recovery_page', user_id=user.id))
    return redirect(url_for('user_profile', user_id=user.id))


@app.route('/email-to-recover', methods=['GET', 'POST'])
def send_email_to_password_recover():
    email_form = EmailForm(prefix='email')
    if request.method == 'POST':
        if email_form.validate():
            user = User.query.filter_by(email=email_form.recovery_email.data).first()
            if not user:
                email_form.recovery_email.errors.append('Wrong email')
                return jsonify({
                    'status': 'errors',
                    'input_errors': email_form.errors
                })

            if user:
                token = generate_confirmation_token(user.id)
                confirm_url = url_for('confirm_user_to_reset_password',
                                      token=token, _external=True)
                html = render_template(
                    "recoverypage/PageToLinkPasswordRecoveryPage.html",
                    confirm_url=str(confirm_url))
                send_email(to=user.email,
                           subject='Forgot you password?',
                           template=html)
                return jsonify({
                    'status': 'ok'
                })
            else:
                email_form.recovery_email.errors.append('Wrong email!')
                return jsonify({
                    'status': 'errors',
                    'input_errors': email_form.errors
                })
        else:
            return jsonify({
                'status': 'errors',
                'input_errors': email_form.errors
            })

    return render_template('recoverypage/EmailToPasswordRecover.html', email_form=email_form)


@app.route('/account/change/password', methods=['POST'])
@login_required
def change_password():
    change_password_form = ChangePasswordForm(
        current_user, prefix='change_password')
    if change_password_form.validate():
        current_user.password = change_password_form.new_password.data
        return jsonify({
            'status': 'ok'
        })
    else:
        return jsonify({
            'status': 'error',
            'input_errors': change_password_form.errors
        })


@app.route('/account/set/phone', methods=['POST'])
@login_required
def set_phone_number():
    set_phone_form = SetPhoneForm(
        current_user,
        prefix='set_phone'
    )

    if set_phone_form.validate():
        status = set_phone_form.type.data
        # Phone is confirmed automatically for now
        if status == '0':
            if not current_user.main_phone:
                current_user.main_phone = set_phone_form.number.data
                current_user.main_phone_confirmed = True
            else:
                set_phone_form.number.errors.append(
                    'You have already set main phone')
                return jsonify({
                    'status': 'error',
                    'input_errors': set_phone_form.errors
                })

        if status == '1':
            if not current_user.extra_phone:
                current_user.extra_phone = set_phone_form.number.data
                current_user.extra_phone_confirmed = True
            else:
                set_phone_form.number.errors.append(
                    'You have already set extra phone')
                return jsonify({
                    'status': 'error',
                    'input_errors': set_phone_form.errors
                })

        # Sending an sms verification(demo, sending only to text twilio phone)
        # new_reserve_number = str(new_reserve_phone_number.number)
        # new_reserve_number_for_sms = new_reserve_number.replace(" ", "")
        # client.sms.messages.create(
        #     body='Confirmation code : 95-85-85-95',
        #     to='+380' + new_reserve_number_for_sms,
        #     from_='+12018957908'
        # )
        # Every new phone number is submitted by default

        return jsonify({
            'status': 'ok'
        })
    else:
        return jsonify({
            'status': 'error',
            'input_errors': set_phone_form.errors
        })


@app.route('/account/delete/phone', methods=['POST'])
@login_required
def phone_delete():
    phone_numbers = request.data
    phone_numbers_dict = json.loads(phone_numbers)
    for phone_number in phone_numbers_dict:
        phone_number_without_spaces = phone_number.replace(' ', '')
        if current_user.main_phone:
            if current_user.main_phone.e164 == phone_number_without_spaces:
                current_user.main_phone = None
        elif current_user.extra_phone:
            if current_user.extra_phone.e164 == phone_number_without_spaces:
                current_user.extra_phone = None

    if phone_numbers_dict:
        return jsonify({
            'status': 'ok'
        })
    else:
        return jsonify({
            'status': 'error',
            'message': 'No phones to delete'
        })

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
