function initServiceContent(getServicesURL,
                            addCreatedServiceURL,
                            addSearchedServicesURL,
                            createSpecialistURL,
                            categories,
                            services){
    initServicesTypeahead(getServicesURL);
    addCreatedService(addCreatedServiceURL);
    addSearchedServices(addSearchedServicesURL);
    $('.become-specialist-btn').on('click', function(){
       createSpecialist(createSpecialistURL);
    });
    initLocationAutocomplete();
    categorySelectorHandler(categories, services);
    addValidationHandlers();
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
                    errorDiv.html(data.errors[i])
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
                    errorDiv.html(data.errors[i])
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
    btn.prop("disabled", selectedServices
            .find('input[id="selected_service_id"]').length <= 0 );
}

function addSearchedServices(addServiceURL){
    toggleAddSelectedServicesBtn();
    $('#search_service_submit').on('click', function () {
        var card = $('#add_service_card');

        var data = {};

        var services = [];
        $('#selected_services')
            .find('input[id="selected_service_id"]')
            .each(function(){
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

function serviceSelectorHandler(services){
    var card = $('#services_card');
    var body = $('body');

    $('#show_service_dropdown').on('click', function(){
        card.show()
    });
    // hide service selector when user click on body
    $(document).mouseup(function (e) {
        var container = $("#service-selector");

        if (!container.is(e.target)
            && container.has(e.target).length === 0) {
            card.hide();
        }
    });

    addServicesToList(services);

    // add service title to main input
    body.find('.service-item').off('click').on('click', function() {
        $('#show_service_dropdown')
            .val($(this).text())
            .addClass('valid');
        $('#selected_service_id')
            .val(_.find(services, {'title': $(this).text()}).id);
        card.hide();
    });
}

function addServicesToList(services){
    var servicesEl = $('#service-selector');
    var servicesList = servicesEl.find('#services_list');

    function addService(title){
        servicesList
            .append(
                '<div class="service-div">' +
                    '<a class="collection-item blue-grey-text text-darken-1 ' +
                        'service-item">' + title + '</a>' +
                '</div>'
        );
    }

    servicesList.empty();

    //Add all services of selected category to list
    _.forEach(services, function(item){
        addService(item.title)
    });

    // Add services which were found by regex to list
    $('#find_service').on('keyup', function(){
        servicesList.empty();
        var matches = findMatches($(this).val(),
            _.map(services, 'title'));
        if (matches.length > 0){
            _.forEach(matches, function(service){
                addService(service)
            });
        } else {
            servicesList
                .append('<a class="collection-item blue-grey-text' +
                        ' text-darken-1">Cannot find service</a>')
        }
    });
}

function findMatches(q, strs){
    // Regex for first letters match

    var regexStartWith = new RegExp("^" + q, 'i');

    var matches = [];
    _.forEach(strs, function(str){
        if (regexStartWith.test(str)) {
            matches.push(str);
        }
    });

    return matches
}


function categorySelectorHandler(categories, services){
    var card = $('#categories_card');
    var body = $('body');

    $('#show_category_dropdown').on('click', function(){
        card.show()
    });

    // hide service selector when user click on body
    $(document).mouseup(function (e) {
        var container = $("#category-selector");

        if (!container.is(e.target)
            && container.has(e.target).length === 0) {
            card.hide();
        }
    });

    addCategoriesToList(categories);

    // add category name to main input
    body.on('click', '.category-item', function() {
        $('#show_category_dropdown')
            .val($(this).text())
            .addClass('valid');
        $('#show_service_dropdown')
            .val('')
            .prop('disabled', false)
            .removeClass('valid');

        $('#selected_service_id').val('');

        card.hide();
        var categoryId = parseInt(
            $(this)
                .closest('.category-div')
                .find('input[class="category-id"]')
                .val()
        );
        // call service selector handler with services for selected category
        serviceSelectorHandler(_.filter(services, {'category_id': categoryId}))
    })
}


function addCategoriesToList(categories){
    var categoriesList = $('#category-selector')
        .find('#categories_list');

    function addCategory(title, id){
        categoriesList
            .append(
            '<div class="category-div">' +
                '<a class="collection-item blue-grey-text text-darken-1 ' +
                    'category-item">' + title + '</a>' +
                '<input type="hidden" class="category-id" value=' + id + '>' +
            '</div>'
        );
    }

    // Add all categories to list
    _.forEach(categories, function(item){
        addCategory(item.title, item.id)
    });

    // Add categories which were found by regex to list
    $('#find_category').on('keyup', function(){
        categoriesList.empty();
        var matches = findMatches($(this).val(), _.map(categories, 'title'));
        if (matches.length > 0){
            _.forEach(matches, function(category){
                var categoryInfo = _.find(categories, {'title': category});
                addCategory(categoryInfo.title, categoryInfo.id)
            });
        } else {
            categoriesList
                .append('<a class="collection-item blue-grey-text' +
                        ' text-darken-1">Cannot find category</a>')
        }
    })
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
