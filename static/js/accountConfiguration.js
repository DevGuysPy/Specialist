function initAccountSettings() {
    checkPasswordFields();
    changePasswrord();
}

function changePasswrord() {
    $('#form-submit').click(function (event) {
        event.preventDefault();
        $('.error').empty();
        $.ajax({
            method: 'POST',
            url: '/account/settings',
            data: $('form').serializeArray()
        }).done(function (response) {
            if (response.status == 'ok') {
                // setTimeout for reload page after materialize toast disappears
                window.setTimeout(function () {
                    location.reload();
                }, 2000);
                $('#company_settings_content').hide();
                Materialize.toast('Password has changed!', 2000);
            } else {
                _.forEach(response.input_errors, function (value, key) {
                    var errorInput = $('#' + key);
                    var errorDiv = $('#error_' + key);
                    errorDiv.html(value);
                    errorInput.attr('class', 'invalid');
                });
            }
        })
    });
}

function checkPasswordFields(){
    var currentPasswordInput = $('#current_password');

    var newPasswordErrorDiv = $('#error_new_password');
    var newPasswordAgainErrorDiv = $('#error_new_password_again');

    var passwordInput = $('#new_password');
    var passwordAgainInput = $('#new_password_again');

    currentPasswordInput.on('keyup', function() {
        newPasswordErrorDiv.empty();
        $(this).removeAttr('class', 'invalid');
    });

    passwordInput.on('keyup', function() {

        newPasswordErrorDiv.empty();
        passwordInput.removeAttr('class', 'invalid');

        if(passwordInput.val() == passwordAgainInput.val()
            || passwordInput.val().length
            >= 4 && passwordInput.val().length <= 64){

            newPasswordErrorDiv.empty();
            newPasswordAgainErrorDiv.empty();
            passwordInput.removeAttr('class', 'invalid');
            passwordAgainInput.removeAttr('class', 'invalid');

        }
        if(passwordInput.val() != passwordAgainInput.val()){

            newPasswordErrorDiv.empty();
            newPasswordAgainErrorDiv.empty();

            passwordInput.attr('class', 'invalid');
            passwordAgainInput.attr('class', 'invalid');

            newPasswordErrorDiv.html('Password does not match');
            newPasswordAgainErrorDiv.html('Password does not match');

        }
        if(passwordInput.val().length <= 4 || passwordInput.val().length >= 64){

            newPasswordAgainErrorDiv.empty();
            newPasswordErrorDiv.empty();

            passwordInput.attr('class', 'invalid');

            newPasswordErrorDiv.html('Field must be between 4 and 64 characters long');

        }
    });

    passwordAgainInput.on('keyup', function() {

        newPasswordAgainErrorDiv.empty();
        passwordAgainInput.removeAttr('class', 'invalid');

        if(passwordInput.val() == passwordAgainInput.val()
            || passwordAgainInput.val().length >= 4
            && passwordAgainInput.val().length <= 64){

            newPasswordErrorDiv.empty();
            newPasswordAgainErrorDiv.empty();

            passwordInput.removeAttr('class', 'invalid');
            passwordAgainInput.removeAttr('class', 'invalid');

        }
        if(passwordInput.val() != passwordAgainInput.val()){

            newPasswordErrorDiv.empty();
            newPasswordAgainErrorDiv.empty();

            passwordInput.attr('class', 'invalid');
            passwordAgainInput.attr('class', 'invalid');

            newPasswordErrorDiv.html('Password does not match');
            newPasswordAgainErrorDiv.html('Password does not match');

        }
        if(passwordAgainInput.val().length <= 4
            || passwordAgainInput.val().length >= 64){

            newPasswordErrorDiv.empty();
            newPasswordAgainErrorDiv.empty();

            passwordAgainInput.attr('class', 'invalid');

            newPasswordAgainErrorDiv.html('Field must be between 4 and 64 characters long');
        }
    });
}