function initServiceActivity(addServiceActivityURL) {
    var card = $('#add_service_activity');
    var preloader = $('.preloader-wrapper');
    $( document ).ready(function() {
        preloader.hide()
    });

    var done = '<p class="btn disabled">' +
        '<i class="material-icons left">done</i>' + SuccessBtn +'</p>';

    $('#service_activity_start').datetimepicker({
      format: 'Y-m-d H:i:00'
    });
    $('#service_activity_end').datetimepicker({
      format: 'Y-m-d H:i:00'
    });

    $('#service_activity_submit').on('click', function () {
        $(this).hide();
        preloader.show();
        var errors = card.find('.error');
        errors.empty();
        $.ajax({
            method: 'POST',
            url: addServiceActivityURL,
            data: $('form').serializeArray()
        }).done(function (data) {
            if (data.status == 'error') {
                errors.empty();
                $('.preloader-wrapper').hide();
                $('#service_activity_submit').show().html(tryAgainBtn);
                var content = card.find('.card-content');
                for (var i in data.errors) {
                    var errorDiv = content
                        .find('#error_service_activity_' + i);
                    errorDiv.html(data.errors[i])
                }
            } else if (data.status == 'ok') {
                $('.preloader-wrapper').hide();
                $('#service_activity_submit')
                    .replaceWith(done)
            }
        });
    });
}