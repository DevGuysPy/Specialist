$(document).ready(function(){
    $('.specialist-form').hide();
    $('.customer-form').hide();
    $(".choice").change(function () {
        var entireForm = $('form');
        var specForm = $('.specialist-form');
        var custForm = $('.customer-form');
        var unusedForm = $('.place_for_unused_form');
        switch ($(this).val()) {
            case 'specialist':
                custForm.hide();
                custForm.appendTo(unusedForm);
                specForm.appendTo(entireForm);
                specForm.show();
                break;
            case 'customer':
                specForm.hide();
                specForm.appendTo(unusedForm);
                custForm.appendTo(entireForm);
                custForm.show();
                break;
        }
    });
    $('.form-submit').click(function(event){
        event.preventDefault();
        $('.error').html('');
        $.ajax({
            method: 'POST',
            url: '/registration/',
            data: $('form').serializeArray()
        }).done(function(response){
            if (response.status == 'ok') {
                document.location.href = "/login/";
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