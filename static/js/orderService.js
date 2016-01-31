function initOrderServiceModal(currentServiceId){
    var modal = $('#order-service-modal');

    initOrderServiceLocAutocomplete(modal);

    var locationAutocomEl = modal.find('#order_service_location_autocomplete');
    var addLocationEl = modal.find('.add-location');
    var locStrEl = modal.find('.selected-location');
    var locDetailsEls = modal.find('input[name]');

    var selectLocationCheckbox = modal.find('#order-service-current-location');
    selectLocationCheckbox.on('click', function(){
       if ( selectLocationCheckbox.is(':checked') ) {
           if (!(window.currentUserLocation)){
               initCurrentUserLocation();
           }
           var address = window.currentUserLocation.formatted_address;
           locationAutocomEl.val(address);
           locationAutocomEl.trigger('geocode');
           locStrEl.text(address);
           addLocationEl.text('Location added').css('color', '#43a047')
       } else {
           locationAutocomEl.val('');
           locDetailsEls.val('');
           locStrEl.text('You have not selected location for your order');
           addLocationEl.text('Add location').css('color', 'inherit')
       }
    });

    google.maps.event.addListener(orderServiceAutocomplete,
            'place_changed', function() {
        locStrEl.text(locationAutocomEl.val());
        addLocationEl.text('Location added').css('color', '#43a047');
        if (window.currentUserLocation.formatted_address &&
                locationAutocomEl.val() !=
                    window.currentUserLocation.formatted_address){
            selectLocationCheckbox.prop('checked', false)
        }
    });

    locationAutocomEl.on('keyup', function(){
        locStrEl.text('You have not selected location for your order');
        addLocationEl.text('Add location').css('color', 'inherit');
        locDetailsEls.val('');
        selectLocationCheckbox.prop('checked', false)
    });

    var locEl = modal.find('.by-interface-location');
    var mainEl = modal.find('.by-interface-main');
    var timeEl = modal.find('.by-interface-timing');
    modal.find('.add-location-btn').on('click', function(){
        mainEl.hide();
        locEl.show().addClass('order-service-animation');
        google.maps.event.trigger(orderServiceMap, "resize")
    });

    modal.find('.hide-location-btn').on('click', function(){
        locEl.hide();
        timeEl.hide();
        mainEl.show().addClass('order-service-animation')
    });

    modal.find('.add-service-timing').on('click', function(){
        mainEl.hide();
        timeEl.show().addClass('order-service-animation');
    });

    function setDatePicker(el, onSetFunc){
        el.pickadate({
            selectMonths: true,
            selectYears: 100,
            format: 'yyyy/mm/dd',
            onSet: function(){
                onSetFunc()
            }
        })
    }

    var timingInfo = modal.find('.timing-info');

    var startInput = modal.find('.start-datepicker');
    setDatePicker(
        startInput,
        function(){
            var info = timingInfo.find('.start-timing-info');
            if (startInput.val()) {
                info
                    .show()
                    .find('.info')
                    .text('Start: ' + startInput.val())
            } else {
                info
                    .hide()
            }
            toggleTimingStr();
        }
    );

    var endInput = modal.find('.end-datepicker');
    setDatePicker(
        endInput,
        function() {
            var info = timingInfo.find('.end-timing-info');
            if (endInput.val()) {
                info
                    .show()
                    .find('.info')
                    .text('End: ' + endInput.val());
            } else {
                info
                    .hide()
            }
            toggleTimingStr();
        }
    );

    var selectTypeTiming = modal.find('.select-timing-type');

    function toggleTimingStr(){
        var addTiming = modal.find('.add-timing');
        if (endInput.val() ||
            startInput.val() ||
            selectTypeTiming.find('option:selected').val() != '0'){
            addTiming.text('Timing changed').css('color', '#43a047')
        } else {
            addTiming.text('Change timing').css('color', 'inherit')
        }
    }

    selectTypeTiming.on('change', function(){
        timingInfo
            .find('.type-timing-info')
            .find('.info')
            .text('Type: ' + $(this).find('option:selected').text());
        toggleTimingStr();
    });


    $('.order-service-btn').on('click', function(){
        var card = $(this).closest('.specialist-card');

        var specCard = modal.find('.order-service-specialist-card');

        modal.on('click', '#add_order', function(){
            addOrder(specCard, $(this));
        });

        modal.on('click', '#order-service-send-msg-btn', function(){
            sendPersonalMsg(specCard, modal, $(this));
        });

        specCard.empty();
        var filters = [
            {
                "name": "user_id",
                "op": "==",
                "val": parseInt(card.find('input[class="user-id"]').val())
            }
        ];
        $.ajax({
            data: {"q": JSON.stringify({"filters": filters})},
            dataType: "json",
            url: '/api/specialist',
            contentType: "application/json"
        }).done(function (data) {
            var spec = _.head(data.objects);
            if (!(spec)){
                return
            }
            var serEl = modal.find('.order-service-services').find('select');
            serEl.empty();
            _.forEach(spec.services, function(item){
                serEl.append(
                    '<option value="' + item.id + '"' +
                    (currentServiceId == item.id ? 'selected' : '') + '>' +
                    item.title + '</option>')
            });
            serEl.material_select();

        });
        card
            .closest('.product')
            .clone()
            .appendTo(specCard)
            .find('.order-service-el')
            .remove();

        $('.sign_up_or_login').on('login', function(){
            $('.sign_up_or_login.login-interface').replaceWith(
               '<a id="add_order" class="waves-effect waves-light btn ' +
               'blue-grey darken-3">Send request</a>');
            $('.sign_up_or_login.login-msg').replaceWith(
               '<a id="order-service-send-msg-btn" class="waves-effect ' +
               'waves-light btn blue-grey darken-3">Send Message</a>');
        });

        modal.openModal();
    });
}

function initOrderServiceLocAutocomplete(modal) {
    var autocompleteInput = modal.find('#order_service_location_autocomplete');
    autocompleteInput.geocomplete({
        map: ".order-service-current-map",
        details: "#order_service_location_details",
        detailsAttribute: "name",
        mapOptions: {
            scrollwheel: true,
            zoom: 3
        },
        markerOptions: {
            draggable: true
        },
        location: [49.337407,29.8229751],
        setGlobal: true
    }).bind("geocode:dragged", function(event, latLng){
        getLocByLatLng(latLng.lat(), latLng.lng(), function(data){
            var address = _.head(data.results).formatted_address;
            autocompleteInput.val(address);
            modal
                .find('#order-service-current-location')
                .prop('checked', false);
            $('.selected-location').text(address);
            $('.add-location').text('Location added').css('color', '#43a047')
        });
    });
    autocompleteInput.attr('placeholder', '')
}

function addOrder(specCard, btn){
    var preloader = initPreloader(btn);
    var data = {};
    data['service_id'] =
        $('.order-service-services').find('option:selected').val();

    data['user_id'] =
        specCard.find('input[class="user-id"]').val();

    data['description'] = $('#order_service_description').val();

    var location = {};
    $('#order_service_location_details')
        .find('input')
        .each(function(){
            location[$(this).attr('name')] = $(this).val()
        });

    data['location'] = location;

    data['start'] = $('#order_service_start').val();
    data['end'] = $('#order_service_end').val();
    data['timing_type'] =
        $('.select-timing-type').find('option:selected').val();
    $.ajax({
        method: 'POST',
        data: JSON.stringify(data),
        dataType: "json",
        url: '/add_order',
        contentType: "application/json",
        success: function(data){
            window.location = data.redirect_url
        },
        error: function(a, b, c){
            preloader.hide();
            btn
                .show()
                .parent()
                .find('.error-message')
                .show()
        }
    })
}

function sendPersonalMsg(card, modal, btn){
    var preloader = initPreloader(btn);
    var data = {};
    data['user_id'] =
        card.find('input[class="user-id"]').val();

    data['subject'] = modal.find('#order_service_message_subject').val();

    data['text'] = modal.find('#order_service_message_text').val();

    var errorEl = $('#by-message-error');
    $.ajax({
        method: 'POST',
        data: JSON.stringify(data),
        dataType: "json",
        url: '/send_message',
        contentType: "application/json",
        success: function(data){
            if (data.status == 'ok') {
                window.location = data.redirect_url
            } else {
                errorEl.text(data.message);
                preloader.hide();
                btn.show()
            }
        },
        error: function(){
            errorEl.text('Ups, something goes wrong.');
            preloader.hide();
            btn.show()
        }
    })
}
