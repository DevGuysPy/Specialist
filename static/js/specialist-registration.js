$(document).ready(function(){
    $(".choice").change(function () {
        switch ($(this).val()) {
            case 'specialist':
                $('.customer-form').hide();
                $('.specialist-form').show();
                break;
            case 'customer':
                $('.specialist-form').hide();
                $('.customer-form').show();
                break;
        }
    });
    $('.form-submit').click(function(event){
        event.preventDefault();
        $('.error').html('');
        $.ajax({
            method: 'POST',
            url: '/specialist-registration/',
            data: $('form').serializeArray()
        }).done(function(response){
            if (response.status == 'ok') {
                var Succeed = $('.done');
                Succeed.html('Success!');
            } else {
                for(var key in response.input_errors) {
                    var errorDiv = $('#error_' + key);
                    errorDiv.html(response.input_errors[key][0])
                }
            }
        })
    });
    $('#conf_pass').on('keyup', function() {
        var pass = $('#pass');
        var conf_pass = $('#conf_pass');
        var message = $('#confirmMessage');

        if(pass.val() == conf_pass.val()){
            message.html('OK');
        }else{
            message.html('Passwords do not match!');
        }
    });
});