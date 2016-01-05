function initServiceActivityModal(addServiceActivityURL) {
    var modal = $('#add_service_activity_modal');

    $('.modal-trigger').leanModal();

    $('#service_activity_start').datetimepicker({
      format: 'Y-m-d H:i:00'
    });
    $('#service_activity_end').datetimepicker({
      format: 'Y-m-d H:i:00'
    });

    $('#service_activity_submit').on('click', function () {
        $(this).html("Working...");
        var errors = modal.find('.error');
        errors.empty();
        $.ajax({
            method: 'POST',
            url: addServiceActivityURL,
            data: $('form').serializeArray()
        }).done(function (data) {
            if (data.status == 'error') {
                errors.empty();
                $('#service_activity_submit').html('Add');
                var modalContent = modal.find('.modal-content');
                for (var i in data.errors) {
                    var errorDiv = modalContent
                        .find('#error_service_activity_' + i);
                    errorDiv.html(data.errors[i])
                }
            } else {
                modal.closeModal();
            }
        });
    });
}