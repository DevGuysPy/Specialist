function initAccountSettings(change_password_url, change_phone_url,
                             set_phone_url, set_reserve_phone_url, change_reserve_phone_url) {
    checkPasswordFields();
    PickForChangeReservePhone();
    phoneFieldEmpty();
    sendEmail();
    //click events for forms' submits
    $('#change-password-submit').click(function(event){
        event.preventDefault();
        adjustSettings(change_password_url, $('#change_password_form'), $('.change_password_error'))
    });

    $('#change-phone-submit').click(function(event){
        event.preventDefault();
        adjustSettings(change_phone_url, $('#change_phone_number_form'), $('.change_phone_error'))
    });

    $('#set-phone-submit').click(function(event){
        event.preventDefault();
        adjustSettings(set_phone_url, $('#set_phone_form'), $('.set_phone_error'))
    });

    $('#set-reserve-phone-submit').click(function(event){
        event.preventDefault();
        adjustSettings(set_reserve_phone_url, $('#set_reserve_phone_form'), $('.set_reserve_phone_error'))
    });

    $('#change-reserve-phone-submit').click(function(event){
        event.preventDefault();
        adjustSettings(change_reserve_phone_url, $('#change_reserve_phone_form'), $('.change_reserve_phone_error'))
    });

}

function phoneFieldEmpty(){

    var setPhoneError = $('.set_phone_error');
    var changePhoneError = $('.change_phone_error');

    var setReservePhoneError = $('.set_reserve_phone_error');
    var changeReservePhoneError = $('.change_reserve_phone_error');

    //'onkeyup' events for phone fields
    $('#set_number').on('keyup', function(){
        setPhoneError.empty();
    });
    $('#change_number').on('keyup', function(){
        changePhoneError.empty()
    });
    $('#set_reserve_number').on('keyup', function(){
        setReservePhoneError.empty();
    });
    $('#new_reserve_number').on('keyup', function(){
        changeReservePhoneError.empty();
    });
}

function PickForChangeReservePhone(){
    $('.reserve_phone').click(function(){
        var reservePhoneNumber = $(this).text();
        $('#old_reserve_number').attr('value', reservePhoneNumber)
    });

}

function adjustSettings(url, form, errorField) {
    errorField.empty();
    $.ajax({
        method: 'POST',
        url: url,
        data: form.serializeArray()
    }).done(function (response) {
        if (response.status == 'ok') {
            var cardContent = $('.card-content');
            cardContent.empty();
            cardContent.html(
                'Settings successfuly applied!<br>'
                );
        } else {
            _.forEach(response.input_errors, function (value, key) {
                var errorInput = $('#' + key);
                var errorDiv = $('#error_' + key);
                errorDiv.html(value[0]);
                errorInput.attr('class', 'invalid');
            });
        }
    })
}


function checkPasswordFields(){
    var currentPasswordInput = $('#current_password');
    var currentPasswordErrorDiv = $('#error_current_password');

    var newPasswordErrorDiv = $('#error_new_password');
    var newPasswordAgainErrorDiv = $('#error_new_password_again');

    var passwordInput = $('#new_password');
    var passwordAgainInput = $('#new_password_again');

    function emptyNewPasswordErrorDiv(){
        newPasswordErrorDiv.empty();
        newPasswordAgainErrorDiv.empty();
    }
    function markValid(){
        passwordInput.removeAttr('class', 'invalid');
        passwordAgainInput.removeAttr('class', 'invalid');
    }

    function markInvalid(){
        passwordInput.attr('class', 'invalid');
        passwordAgainInput.attr('class', 'invalid');

    }

    function raiseErrorMessage(){
        newPasswordErrorDiv.html('Password does not match');
        newPasswordAgainErrorDiv.html('Password does not match');
    }

    currentPasswordInput.on('keyup', function() {
        currentPasswordErrorDiv.empty();
        $(this).removeAttr('class', 'invalid');
    });

    passwordInput.on('keyup', function() {

        if(passwordInput.val() == passwordAgainInput.val()
            && passwordInput.val().length
            >= 8 && passwordInput.val().length <= 64){
            emptyNewPasswordErrorDiv();
            markValid();
        }
        if(passwordInput.val() != passwordAgainInput.val()){
            emptyNewPasswordErrorDiv();
            markInvalid();
            raiseErrorMessage();
        }
        if(passwordInput.val().length < 8 || passwordInput.val().length > 64){
            emptyNewPasswordErrorDiv();
            markInvalid();
            newPasswordErrorDiv.html('Field must be between 8 and 64 characters long');

        }
    });

    passwordAgainInput.on('keyup', function() {

        if(passwordInput.val() == passwordAgainInput.val()
            && passwordAgainInput.val().length >= 8
            && passwordAgainInput.val().length <= 64){
            emptyNewPasswordErrorDiv();
            markValid();
        }
        if(passwordInput.val() != passwordAgainInput.val()){
            emptyNewPasswordErrorDiv();
            markInvalid();
            raiseErrorMessage();

        }
        if(passwordAgainInput.val().length < 8
            || passwordAgainInput.val().length > 64){
            emptyNewPasswordErrorDiv();
            passwordAgainInput.attr('class', 'invalid');
            newPasswordAgainErrorDiv.html('Field must be between 8 and 64 characters long');
        }
    });
}