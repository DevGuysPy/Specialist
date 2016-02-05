function initAccountSettings(change_password_url, set_phone_url) {
    checkPasswordFields();
    phoneFieldEmpty();
    deletePhone();
    //click events for forms' submits
    $('#change-password-submit').click(function(event){
        event.preventDefault();
        $('#cd-popup-pass').addClass('is-visible');
        $('#accept-pass').click(function(){
            adjustSettings(change_password_url, $('#change_password_form'), $('.change_password_error'))
        });
    });

    $('#set-phone-submit').click(function(event){
        event.preventDefault();
        adjustSettings(set_phone_url, $('#set_phone_form'), $('.set_phone_error'))
    });
    $('#set_number').mask('+38(000)000-0000')

}

//press on X or escape to remove pop-remove
function removePopUp() {

    $(document).on('keyup', function(event){
    	if(event.which=='27'){
    		$('.cd-popup').removeClass('is-visible');
	    }
    });
    $('.cd-popup').on('click', function(event){
        $(this).removeClass('is-visible');
	});
}

function deletePhone(){

    var initButton = $('#delete');
    initButton.addClass('disabled');
    var checkBox = $(':checkbox[name="phone"]');

    //enabling delete button
    //if one checkbox is checked at least ==> remove disable style
    checkBox.click(function(){
        if ($('#phone1').is(':checked') || $('#phone2').is(':checked') ) {
            initButton.removeClass('disabled');
        }else{
            initButton.addClass('disabled');
        }
    });
    removePopUp();

    initButton.click(function(){
        var phonesToDelete = [];
        var checkedBoxes = $("input:checkbox[name=phone]:checked");
        checkedBoxes.each(function(){
            phonesToDelete.push(this.value)
        });

        $('#cd-popup-contacts').addClass('is-visible');

        $('#accept-contacts').click(function(){
            $.ajax({
            method: 'POST',
            url: '/account/delete/phone',
            data: JSON.stringify(phonesToDelete),
            dataType: "json",
            contentType: "application/json"
        }).done(function (response) {
            if (response.status == 'ok') {
                 location.reload();
            }else{
                alert('Removing the disabled class is not a good idea')
            }
        });
        });
    });
}

function phoneFieldEmpty() {

    var setPhoneError = $('.set_phone_error');

    var setReservePhoneError = $('.set_reserve_phone_error');

    //'onkeyup' events for phone fields
    $('#set_number').on('keyup', function () {
        setPhoneError.empty();
    });
    $('#set_reserve_number').on('keyup', function () {
        setReservePhoneError.empty();
    });
}

function adjustSettings(url, data, errorField) {
    errorField.empty();
    $.ajax({
        method: 'POST',
        url: url,
        data: data.serializeArray()
    }).done(function (response) {
        if (response.status == 'ok') {
            location.reload();
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