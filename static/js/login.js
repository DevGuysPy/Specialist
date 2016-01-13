function initLogin(loginSubmitURL){
    $('#login_submit').on('click', function(){
        basicSignUpAjaxCall(loginSubmitURL)
    })
}

function basicSignUpAjaxCall(URL){
    var card = $('.login-card');
    var errors = card.find('.error');
    $.ajax({
        method: 'POST',
        url: URL,
        data: $('#login_form').serializeArray()
    }).done(function (data) {
        if (data.status == 'error') {
            errors.empty();
            for (var i in data.errors) {
                var errorDiv = card
                    .find('#error_login_' + i);
                errorDiv.html(data.errors[i])
            }
            if (data.send_confirmation_email_url){
                var confErrorEl = card.find('#error_login_password');
                confErrorEl.html(
                    'Confirm your email to log in<br>' +
                    '<a id="login_send_conf_email">Send email again</a>'
                );
                $('#login_send_conf_email').on('click', function(){
                    $.ajax({
                        method: 'POST',
                        url: data.send_confirmation_email_url
                    }).done(function(){
                        confErrorEl
                            .html('Email was sent')
                            .css('color', '#00c853')
                    })
                })
            }
        } else {
            window.location = data.login_success_url;
        }
    });
}