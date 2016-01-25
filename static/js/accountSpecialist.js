function initServiceContent(addServicesURL,
                            createSpecialistURL,
                            categoryApiURL,
                            serviceApiURL){
    addSpecServices(addServicesURL);
    $('.become-specialist-btn').on('click', function(){
       createSpecialist(createSpecialistURL);
    });
    initLocationAutocomplete();
    addValidationHandlers();
    initInputAutocomplete(
        $('#show_category_dropdown'),
        categoryApiURL,
        {},
        function (suggestion) {
            $('#show_service_dropdown').prop('disabled', false);
            $('#show_category_dropdown')
                .removeClass('invalid')
                .addClass('valid');
            initServiceSelector(suggestion.data, serviceApiURL)
        });
    initInputAutocomplete(
        $('#add_specialist_services'),
        serviceApiURL,
        {},
        function(suggestion){
            addServiceTag($('#selected_services'),
                suggestion.data, suggestion.value);

        })
}

function createSpecialist(URL){
    var card = $('.create-specialist-card');
    $('.become-specialist-card').hide();
    card.show();
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

function toggleAddSelectedServicesBtn(){
    var btn = $('#search_service_submit');
    var selectedServices = $('#selected_services');
    btn.prop("disabled", selectedServices
            .find('input[id="selected_service_id"]').length <= 0 );
}

function addSpecServices(addServiceURL){
    toggleAddSelectedServicesBtn();
    $('#search_service_submit').on('click', function () {
        var selectedServiceEl = $('#selected_services');
        var card = $('#add_service_card');

        var data = {};

        var services = [];
        selectedServiceEl
            .find('input[id="selected_service_id"]')
            .each(function(){
                services.push($(this).val())
            });
        selectedServiceEl.empty();
        $('#add_specialist_services').val('');

        data['selected_service_ids'] = services;

        $.ajax({
            method: 'POST',
            url: addServiceURL,
            data: JSON.stringify(data),
            dataType: "json",
            contentType: "application/json"
        }).done(function (data) {
            if (data.status == 'error') {
              card.append('<p>Houston, we have a problem</p>')
            } else {
                _.each(data.services, function(item){
                    addServiceToAccordion(item)
                });
                toggleAddSelectedServicesBtn();
            }
        });
    });
}

function addServiceToAccordion(service){
    var accordion = $('#services_accordion');
    $('.specialist-services').show();
    $(".no-services-services").hide();
    var serviceEl =
        '<li>' +
            '<div class="collapsible-header service-accordion">' +
            service.name +
            '</div>' +
            '<div class="collapsible-body service-accordion">' +
            '<p>Cool information</p>' +
            '</div>' +
        '</li>';
    accordion.prepend(serviceEl)
}

function addServiceTag(div, serviceId, serviceName){
    if ($('input[id="selected_service_id"][value="' + serviceId + '"]').length){
        return
    }
    div.append('<div class="selected-service">' +
        '<input type="hidden" value="' + serviceId + '" id="selected_service_id">' +
        '<div class="chip service-tag">' +
            serviceName +
            '<i class="material-icons close-tag">close</i>' +
        '</div>' +
    '</div>');
    closeTagHandler();
    toggleAddSelectedServicesBtn();
}

function closeTagHandler(){
    $('.close-tag').on('click', function(){
        $(this).closest('.selected-service').remove();
        toggleAddSelectedServicesBtn();
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
    var serviceInput = $('#show_service_dropdown');
    var categoryInput = $('#show_category_dropdown');
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
