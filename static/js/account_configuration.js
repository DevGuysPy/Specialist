/**
 * Created by yura on 17.01.16.
 */

$(document).ready(function(){
    $('#form-submit').click(function(event){
        event.preventDefault();
        $('.error').empty();
        $.ajax({
            method: 'POST',
            url: '/account/settings',
            data: $('form').serializeArray()
        }).done(function(response){
            if (response.status == 'ok') {
                window.setTimeout(function () {
                    location.reload();
                }, 2000);
                $('#company_settings_content').hide();
                Materialize.toast('Password has changed!', 2000);
            } else {
                for(var key in response.input_errors) {
                    var errorInput = $('#' + key);
                    var errorDiv = $('#error_' + key);
                    errorDiv.html(response.input_errors[key][0])
                    errorInput.attr('class', 'invalid');
                }
            }
        })
    });
    $('#current_password').on('keyup', function() {
        var errorDiv = $('#error_current_password');
        errorDiv.empty();
        $(this).removeAttr('class', 'invalid');
    });
    $('#new_password').on('keyup', function() {
        var new_password_errorDiv = $('#error_new_password');
        var new_password_again_errorDiv = $('#error_new_password_again');

        var passwordInput = $('#new_password');
        var password_againInput = $('#new_password_again');

        new_password_errorDiv.empty();
        passwordInput.removeAttr('class', 'invalid');

        if(passwordInput.val() == password_againInput.val()
            || passwordInput.val().length
            >= 4 && passwordInput.val().length <= 64){

            new_password_errorDiv.empty();
            new_password_again_errorDiv.empty();
            passwordInput.removeAttr('class', 'invalid');
            password_againInput.removeAttr('class', 'invalid');

        }
        if(passwordInput.val() != password_againInput.val()){

            new_password_errorDiv.empty();
            new_password_again_errorDiv.empty();

            passwordInput.attr('class', 'invalid');
            password_againInput.attr('class', 'invalid');

            new_password_errorDiv.html('Password do not match');
            new_password_again_errorDiv.html('Password do not match');

        }
        if(passwordInput.val().length <= 4 || passwordInput.val().length >= 64){

            new_password_again_errorDiv.empty();
            new_password_errorDiv.empty();

            passwordInput.attr('class', 'invalid');

            new_password_errorDiv.html('Field must be between 4 and 64 characters long');

        }
    });

    $('#new_password_again').on('keyup', function() {

        var new_password_errorDiv = $('#error_new_password');
        var new_password_again_errorDiv = $('#error_new_password_again');

        var passwordInput = $('#new_password');
        var password_againInput = $('#new_password_again');

        new_password_again_errorDiv.empty();
        password_againInput.removeAttr('class', 'invalid');

        if(passwordInput.val() == password_againInput.val()
            || password_againInput.val().length >= 4
            && password_againInput.val().length <= 64){

            new_password_errorDiv.empty();
            new_password_again_errorDiv.empty();

            passwordInput.removeAttr('class', 'invalid');
            password_againInput.removeAttr('class', 'invalid');

        }
        if(passwordInput.val() != password_againInput.val()){

            new_password_errorDiv.empty();
            new_password_again_errorDiv.empty();

            passwordInput.attr('class', 'invalid');
            password_againInput.attr('class', 'invalid');

            new_password_errorDiv.html('Passwords do not match');
            new_password_again_errorDiv.html('Passwords do not match');

        }
        if(password_againInput.val().length <= 4
            || password_againInput.val().length >= 64){

            new_password_again_errorDiv.empty();
            new_password_errorDiv.empty();

            password_againInput.attr('class', 'invalid');

            new_password_again_errorDiv.html('Field must be between 4 and 64 characters long');
        }
    });
});