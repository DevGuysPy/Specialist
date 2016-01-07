function initSignUp(signUpURL, getServicesURL, specSignUpURL, addServiceURL){
    $('#sign_up_password, #sign_up_confirm_password').on('keyup', function(){
        if ($('#sign_up_password').val() !== $('#sign_up_confirm_password').val()){
            $('#error_sign_up_password').html(
                'Passwords must match').css('color', '#f06292');
        } else {
            $('#error_sign_up_password').html('');
        }
    });
    $('#sign_up_submit_basic').on('click', function(){
        basicSignUpAjaxCall(signUpURL, function(data){
            window.location = 'user/' + data.user_id + '/profile'
        })
    });
    $('#sign_up_submit_spec').on('click', function(){
        basicSignUpAjaxCall(signUpURL, function(data){
            $('.first-step-sign-up').hide();
            $('.add-services-sign-up').show();
            initServicesTypeahead(getServicesURL);
            initSpecSignUp(specSignUpURL);
            initAddServiceModal(addServiceURL);
        })
    });
}


function basicSignUpAjaxCall(URL, successFunc){
    var card = $('.first-step-sign-up');
    var errors = card.find('.error');
    $.ajax({
        method: 'POST',
        url: URL,
        data: $('#basic_sign_up_form').serializeArray()
    }).done(function (data) {
        if (data.status == 'error') {
            errors.empty();
            for (var i in data.errors) {
                var errorDiv = card
                    .find('#error_sign_up_' + i);
                errorDiv.html(data.errors[i]).css('color', '#f06292')
            }
        } else {
            successFunc(data)
        }
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

function addServiceTag(div, serviceId, serviceName){
    div.append('<div class="selected-service">' +
        '<input type="hidden" value="' + serviceId + '" id="selected_service_id">' +
        '<div class="chip">' +
            serviceName +
            '<i class="material-icons close-tag">close</i>' +
        '</div>' +
    '</div>');
    closeTagHandler();
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
        typeaheadEl.css('width', '865px');
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

function closeTagHandler(){
    $('.close-tag').on('click', function(){
        $(this).closest('.selected-service').remove()
    })
}


function initSpecSignUp(signUpURL){
    $('#spec_sign_up_submit').on('click', function(){
        specSignUpCall(signUpURL, function(data){
            window.location = 'user/' + data.user_id + '/profile'
        })
    });
}

function specSignUpCall(URL,successFunc){
    var card = $('.add-services-sign-up');
    var errors = card.find('.error');
    //var data = {};
    //data['form'] = $('#spec_sign_up_form').serializeArray();
    var form = $('#spec_sign_up_form').serializeArray();
    var services = [];
    $('#selected_services').find('input[id="selected_service_id"]').each(function(){
        services.push($(this).val())
    });
    if (services.length > 0) {
        form.push({'name': 'services', 'value': services});
    } else {
        var errorSelector = card.find('#error_sign_up_service_selector');
        errorSelector
            .html('Enter et least 1 service you offer')
            .css('color', '#f06292');
        $('#sign_up_service_selector').on('click', function(){
            errorSelector.html('')
        });
        return {}
    }
    $.ajax({
        method: 'POST',
        url: URL,
        data: form
    }).done(function (data) {
        if (data.status == 'error') {
            errors.empty();
            for (var i in data.errors) {
                var errorDiv = card
                    .find('#error_sign_up_' + i);
                errorDiv.html(data.errors[i]).css('color', '#f06292')
            }
        } else {
            successFunc(data)
        }
    });
}

function initAddServiceModal(addServiceURL){
    $('#open_service_modal').on('click', function(){
        $('#add_service_modal').openModal()
    });

    var modal = $('#add_service_modal');
    $('#service_submit').on('click', function () {
        var errors = modal.find('.error');
        errors.empty();
        $.ajax({
            method: 'POST',
            url: addServiceURL,
            data: $('#add_service_form').serializeArray()
        }).done(function (data) {
            if (data.status == 'error') {
                errors.empty();
                $('#service_activity_submit').html('Add');
                var modalContent = modal.find('.modal-content');
                for (var i in data.errors) {
                    var errorDiv = modalContent
                        .find('#error_service_' + i);
                    errorDiv.html(data.errors[i]).css('color', '#f06292')
                }
            } else {
                addServiceTag(
                    $('#selected_services'),
                    data.service.id,
                    data.service.name);
                modal.closeModal();
            }
        });
    });
}