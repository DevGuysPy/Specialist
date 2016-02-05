function initSpecCreation(createSpecialistURL,
                            categoryApiURL,
                            serviceApiURL){
    createSpecialist(createSpecialistURL);
    initLocationAutocomplete();
    addValidationHandlers();
    initInputAutocomplete(
        $('#category_selector'),
        categoryApiURL,
        {},
        function (suggestion) {
            $('#service_selector').prop('disabled', false);
            $('#category_selector')
                .removeClass('invalid')
                .addClass('valid');
            initServiceSelector(suggestion.data, serviceApiURL)
        });
}

function createSpecialist(URL){
    var card = $('.create-specialist-card');
    var errors = card.find('.error');

    $('#specialist_submit').on('click', function(){
        $.ajax({
            method: 'POST',
            url: URL,
            data: $('#specialist_form').serializeArray()
        }).done(function (data) {
            if (data.status == 'error') {
                errors.empty();
                for (var i in data.errors) {
                    var errorDiv = card
                        .find('#error_specialist_' + i);
                    errorDiv.html(data.errors[i])
                }
            } else {
                window.location.reload()
            }
        });
    });
}

function initLocationAutocomplete() {
    var autocompleteInput = $('#location_autocomplete');
    autocompleteInput.geocomplete({
        details: "#location_details",
        detailsAttribute: "location_attr"
    });
    autocompleteInput.attr('placeholder', '')
}

function addValidationHandlers(){
    $('#specialist_phone').on('keyup', function(){
        $(this).val().length == 13 ?
            $(this).removeClass('invalid').addClass('valid') :
            $(this).removeClass('valid').addClass('invalid')
    });
    $('.materialize-textarea').on('keyup', function(){
        $(this).val().length < 5000 ?
            $(this).removeClass('invalid').addClass('valid') :
            $(this).removeClass('valid').addClass('invalid')
    });
    $('#location_autocomplete').change(function(){
        $(this).addClass('valid');
    });
    $('#specialist_experience').change(function(){
        $(this)
            .closest('.select-wrapper')
            .find('input[type="text"]')
            .addClass('valid');
    });
}

function initServiceSelector(categoryId, apiURL){
    var serviceInput = $('#service_selector');
    var categoryInput = $('#category_selector');
    var selectedServiceIdEl = $('#selected_service_id');

    categoryInput.on('keyup', function(){
        serviceInput.prop('disabled', true);
        categoryInput.addClass('invalid');
        selectedServiceIdEl.val('');
    });
    serviceInput.on('keyup', function(){
        serviceInput.addClass('invalid');
        selectedServiceIdEl.val('');
    });

    initInputAutocomplete(
        serviceInput,
        apiURL,
        {'category': categoryId},
        function (suggestion) {
            $('#selected_service_id')
                .val(suggestion.data);
            serviceInput.addClass('valid').removeClass('invalid');
        });
}