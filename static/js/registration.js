function initSignUp(signUpURL){
    $('#sign_up_submit_basic').on('click', function () {
        basicSignUpAjaxCall(signUpURL)
    });
}


function basicSignUpAjaxCall(URL){
    var card = $('.first-step-sign-up');
    var errors = card.find('.error');
    $.ajax({
        method: 'POST',
        url: URL,
        data: $('#basic_sign_up_form').serializeArray()
    }).done(function (data) {
        if (data.status == 'error') {
            errors.empty();
            for (var i in data.errors) {
                var errorDiv = card
                    .find('#error_sign_up_' + i);
                errorDiv.html(data.errors[i])
            }
        } else {
            window.location = '/login'
        }
    });
}