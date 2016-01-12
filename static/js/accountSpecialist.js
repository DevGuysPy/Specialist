function initServiceContent(getServicesURL,
                        addCreatedServiceURL,
                        addSearchedServicesURL,
                        createSpecialistURL){
    initServicesTypeahead(getServicesURL);
    addCreatedService(addCreatedServiceURL);
    addSearchedServices(addSearchedServicesURL);
    $('.become-specialist-btn').on('click', function(){
       createSpecialist(createSpecialistURL);
    });
}


function substringMatcher(strs) {
    return function findMatches(q, cb) {
        var matches, substringRegex;

        // an array that will be populated with substring matches
        matches = [];

        // regex used to determine if a string contains the substring `q`
        var regexStartWith = new RegExp("^" + q, 'i');


        // iterate through the pool of strings and for any string that
        // contains the substring `q`, add it to the `matches` array
        $.each(strs, function (i, str) {
            if (regexStartWith.test(str) && matches.length < 5 ) {
                matches.push(str);
            }
        });

        cb(matches);
    };
}

function initServicesTypeahead(URL){
    var typeaheadEl = $('#sign_up_service_selector');
    $.ajax({
        method: 'GET',
        url: URL
    }).done(function (data) {
        var serviceNames = [];
        _.each(data.services, function(item){
            serviceNames.push(item['name'])
        });
        typeaheadEl.typeahead({
                hint: true,
                highlight: true,
                minLength: 1
            },
            {
                name: 'services',
                source: substringMatcher(serviceNames)
            });
        typeaheadEl.css('width', '700px');
        typeaheadEl.parent().append(
            '<label for="sign_up_service_selector">' +
            'Search services you offer</label>');

        var selectedServicesDiv = $('#selected_services');
        typeaheadEl.on('typeahead:select', function () {
            var serviceId = parseInt(
                data.services[_.findIndex(data.services, {'name': $(this).val()})]['id']);
            if (selectedServicesDiv
                    .find('input[value="'+ serviceId +'"][id="selected_service_id"]')
                    .length == 0) {
                addServiceTag(selectedServicesDiv, serviceId, $(this).val());

            }
        });
    });
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
                    errorDiv.html(data.errors[i]).css('color', '#f06292')
                }
            } else {
                window.location.reload()
            }
        });
    });
}

function addCreatedService(addServiceURL){
    var card = $('#add_service_card');

    $('#service_submit').on('click', function () {
        var errors = card.find('.error');
        errors.empty();
        $.ajax({
            method: 'POST',
            url: addServiceURL,
            data: $('#add_service_form').serializeArray()
        }).done(function (data) {
            if (data.status == 'error') {
                errors.empty();
                $('#service_activity_submit').html('Add');
                for (var i in data.errors) {
                    var errorDiv = card
                        .find('#error_service_' + i);
                    errorDiv.html(data.errors[i]).css('color', '#f06292')
                }
            } else {
                addServiceToAccordion(data.service)
            }
        });
    });
}

function toggleAddSelectedServicesBtn(){
    var btn = $('#search_service_submit');
    var selectedServices = $('#selected_services');
    selectedServices.find('input[id="selected_service_id"]').length > 0 ?
        btn.prop("disabled", false) : btn.prop("disabled", true);
}

function addSearchedServices(addServiceURL){
    toggleAddSelectedServicesBtn();
    $('#search_service_submit').on('click', function () {
        var card = $('#add_service_card');

        var data = {};

        var services = [];
        $('#selected_services').find('input[id="selected_service_id"]').each(function(){
            services.push($(this).val())
        });
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
    div.append('<div class="selected-service">' +
        '<input type="hidden" value="' + serviceId + '" id="selected_service_id">' +
        '<div class="chip">' +
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
