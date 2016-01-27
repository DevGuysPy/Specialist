function initServiceContent(addServicesURL, serviceApiURL){
    addSpecServices(addServicesURL);
    initInputAutocomplete(
        $('#add_specialist_services'),
        serviceApiURL,
        {},
        function(suggestion){
            addServiceTag($('#selected_services'),
                suggestion.data, suggestion.value);

        })
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