function recoveryPageInit() {
    var errorField = $('.errors');
    sendEmailToRecover(errorField);
    changePasswordViaRecovery(errorField);
}
function sendEmailToRecover(errorField){

    var sendEmailButton = $('#send_email_to_password_recover');
    var emailForm = $('#email_form');

    sendEmailButton.click(function(event){
        errorField.empty();
        event.preventDefault();
        $.ajax({
            method: 'POST',
            url: '/email-to-recover',
            data: emailForm.serializeArray()
        }).done(function (response) {
            if (response.status == 'ok') {

                //After succeed ==> card reveal closes
                var emailCardReveal = $('#email-card-reveal');
                emailCardReveal.css('display', 'none');
                emailCardReveal.css('transform', 'translateY(0px)');
                Materialize.toast('Sent', 2000);

                // Condition checking if user is on '/email to recover' url - url
                // when user link to "Forgot Password" at the login page.
                // Timeout is used to  message a user an email has been sent
                // - then follows the reloading of a page to "/login"
                if(document.location.pathname == '/email-to-recover'){
                    window.setTimeout(function(){
                        location.href = '/login';
                    }, 2000);
                }
            } else {
                _.forEach(response.input_errors, function (value, key) {
                    var errorInput = $('#' + key);
                    var errorDiv = $('#error_' + key);
                    errorDiv.html(value[0]);
                    errorInput.attr('class', 'invalid');
                });
            }
        })
    })


}
function changePasswordViaRecovery(errorField){
    var changePasswordButton = $('#password_via_recover_btn');
    var changePasswordForm = $('#password_form');
    changePasswordButton.click(function(event){
        errorField.empty();
        event.preventDefault();
        $.ajax({
            method: 'POST',
            url: '/reset-password',
            data: changePasswordForm.serializeArray()
        }).done(function (response) {
            if (response.status == 'ok') {
                window.location = '/login';
                if(document.location.pathname == '/login'){
                    Materialize.toast('Password has been changed', 2000);
                }
            } else {
                _.forEach(response.input_errors, function (value, key) {
                    var errorInput = $('#' + key);
                    var errorDiv = $('#error_' + key);
                    errorDiv.html(value[0]);
                    errorInput.attr('class', 'invalid');
                });
            }
        })
    });


}