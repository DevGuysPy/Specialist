function initServiceActivity(addServiceActivityURL) {
    var card = $('#add_service_activity');
    var preloader = '<div class="preloader-wrapper small active">' +
                        '<div class="spinner-layer spinner-green-only">' +
                          '<div class="circle-clipper left">' +
                            '<div class="circle"></div>' +
                          '</div><div class="gap-patch">' +
                            '<div class="circle"></div>' +
                          '</div><div class="circle-clipper right">' +
                            '<div class="circle"></div>' +
                          '</div></div></div>';
    var done = '<p class="btn disabled">' +
        '<i class="material-icons left">done</i>Request successfully sent</p>'

    $('#service_activity_start').datetimepicker({
      format: 'Y-m-d H:i:00'
    });
    $('#service_activity_end').datetimepicker({
      format: 'Y-m-d H:i:00'
    });

    $('#service_activity_submit').on('click', function () {
        $(this).hide()
        .after(preloader);
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
                $('#service_activity_submit').show().html('try again to Send request');
                var Content = card.find('.card-content');
                for (var i in data.errors) {
                    var errorDiv = Content
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