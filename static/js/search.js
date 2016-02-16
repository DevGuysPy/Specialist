function initSearchPage(currentServiceId,
                        specialistsCount,
                        currentPage,
                        expTypes,
                        requestArgs){
    specialistCardHandler();
    paginationHandler(currentServiceId, specialistsCount, currentPage, requestArgs);
    initOrderByLocation(requestArgs);
    initOrderByExperience(expTypes, requestArgs);
    initOrderBySuccess(requestArgs);
    redirectWithSortParams(currentServiceId);
    showPreviousChips(requestArgs, expTypes);

    $('#chips-container').on('click', '.material-icons', function(){
        $(this).closest('.search-chip').remove()
    })
}

function specialistCardHandler(){
    var cards = $('.specialist-card');
    cards.find('.btn-price, .profile-trigger').on('click', function(){
        window.location = '/account/' + $(this)
                .closest('.specialist-card')
                .find('input[class="user-id"]')
                .val()
    });


    function limitText(el){
        var text = el.text();
        el.text(text.substr(0, 150));
        el.append(' <a class="show-description">Show more</a>' +
        '<span class="hidden-text" style="display: none;">' +
            text.substr(150 , text.length) + '</span>');
    }
    cards.each(function(){
        var textEl = $(this)
            .find('.description')
            .find('.description-text');
        textEl.text().length >= 150 ?
             limitText(textEl): null
    });

    $('.show-description').on('click', function(e){
        $(this).hide();
        $(this).parent().find('.hidden-text').show()
    });

    $('.show-phone').on('click', function(e){
        $(this).hide();
        $(this).parent().find('.phone').show()
    });
}

function paginationHandler(
        currentServiceId, specialistsCount, currentPage, args) {
    var pagesCount = parseInt(specialistsCount / 12);
    if (specialistsCount - pagesCount * 12 != 0) {
        pagesCount = pagesCount + 1
    }

    var pagination = $('.page-numbers');

    var params = '?';
        if (args) {
            for (var key in args) {
                if (key != 'page') {
                    params += key + '=' + args[key] + '&'
                }
            }
        }
    _.forEach(_.range(1, pagesCount + 1), function (pageNum) {
        pagination.append(
            '<li class="waves-effect page-number">' +
            '<a href="/service/' + currentServiceId + params + 'page='
            + pageNum + '" id="' + pageNum + '">' + pageNum + '</a>' +
            '</li>')
    });

    var pageNumberEl = $('.page-number');

    if (currentPage > 5){
        pageNumberEl.slice(1, currentPage - 5).hide();
    }
    if (currentPage < pagesCount - 5) {
        pageNumberEl.slice(currentPage + 4, pagesCount - 1).hide();
    }

    var nextEl = $('#next_page');
    var previousEl = $('#previous_page');
    pageNumberEl.removeClass('active');
    pageNumberEl.find('a#' + currentPage).closest('li').addClass('active');
    if (currentPage == 1) {
        previousEl.find('a').addClass('disabled');
        previousEl.addClass('disabled');
    } else {
        previousEl.find('a').removeClass('disabled');
        previousEl.removeClass('disabled');
    }

    if (currentPage == pagesCount) {
        nextEl.find('a').addClass('disabled');
        nextEl.addClass('disabled');
    } else {
        nextEl.find('a').removeClass('disabled');
        nextEl.removeClass('disabled');
    }
}

function addChip(chipData, inputName, inputVal){
    // function which creates tags with given params
    var container = $('#chips-container');
    chipData = chipData.length > 27? chipData.slice(0, 27) + '...': chipData;
    var chip = $(
        '<div class="search-chip">' +
        '<div class="chip">' +
         chipData +
        '<i class="material-icons">close</i>' +
        '</div>' +
        '<input name="' + inputName + '" value="' + inputVal + '" type="hidden">' +
        '</div');

    if (container.find('input[name="' + inputName + '"]').length) {
        container
            .find('input[name="' + inputName + '"]')
            .closest('.search-chip').replaceWith(chip);
    } else (
        container.append(chip)
    )
}

function initOrderByLocation(args){
    var modal = $('#map-modal');
    var extendedLocInput = $('#order_by_location_autocomplete');
    var cityInput = $('#order_by_location_city_autocomplete');
    var submitBtn = $('#order_by_location_submit');
    var radiusInput = $('#order_by_location_radius');
    var chipsContainer = $('#chips-container');

    // init location autocomplete only for city
    cityInput.geocomplete({
        details: "#order_by_location_city_details",
        detailsAttribute: "name",
        autocompleteOnlyCities: true,
        setGlobal: 'orderingSearchCity'
    });

    // add listener for adding city and country which were selected by user
    // to orderByData
    var cityDetails = $('#order_by_location_city_details');
    google.maps.event.addListener(orderingSearchCityLocObj.autocomplete,
            'place_changed', function () {
        if (chipsContainer.find('input[name="lat_lng"]') ||
                chipsContainer.find('input[name="radius"]')){
            chipsContainer
                .find('input[name="lat_lng"]')
                .closest('.search-chip')
                .remove();
            chipsContainer
                .find('input[name="radius"]')
                .closest('.search-chip')
                .remove();
        }
        var city = cityDetails.find('input[name="locality"]').val();
        var country = cityDetails.find('input[name="country"]').val();
        addChip(
            'In ' + city + ', ' + country,
            'city_loc',
            city + ',' + country)
    });



    // init extended location autocomplete and map
    var openMapModalBtn = $('.select-loc-map');
    extendedLocInput.geocomplete({
        map: '#order-by-location-map',
        details: "#order_by_location_extended_details",
        detailsAttribute: "name",
        setGlobal: 'orderingSearch',
        mapOptions: {
            scrollwheel: true,
            zoom: 3
        },
        markerOptions: {
            draggable: true
        },
        location: [49.337407, 29.8229751],
    }).bind("geocode:dragged", function (event, latLng) {
        getLocByLatLng(
            latLng.lat(),
            latLng.lng(),
            function (address) {
                // add position of marker to location input when marker is moved
                extendedLocInput.val(address.formatted_address);
                extendedLocInput.trigger('geocode');
                submitBtn.removeClass('disabled');
                radiusInput.prop('disabled', false);
            }
        );
    });

    // init radius in center of marker
    var circle = new google.maps.Circle({
        strokeColor: '#37474f',
        strokeOpacity: 0.8,
        strokeWeight: 2,
        fillColor: '#37474f',
        fillOpacity: 0.35,
        map: orderingSearchLocObj.map,
        draggable: true,
        center: {
            'lat': orderingSearchLocObj.marker.getPosition().lat(),
            'lng': orderingSearchLocObj.marker.getPosition().lng()
        },
        radius: 0,
        visible: false,
    });
    circle.bindTo('center', orderingSearchLocObj.marker, 'position');
    google.maps.event.addListener(circle, 'dragend', function () {
        var center = circle.getCenter();
        getLocByLatLng(
            center.lat(),
            center.lng(),
            function (address) {
                // add position of marker to location input when circle is moved
                extendedLocInput.val(address.formatted_address);
                extendedLocInput.trigger('geocode');
                submitBtn.removeClass('disabled');
                radiusInput.prop('disabled', false);
            }
        );
    });

    radiusInput.on('keyup mouseup', function () {
        // show circle when user has entered radius
        circle.setVisible(true);
        this.value >= 0 ? circle.setRadius(this.value * 1000) : null
    });

    google.maps.event.addListener(orderingSearchLocObj.autocomplete,
        'place_changed', function () {
            submitBtn.removeClass('disabled');
            radiusInput.prop('disabled', false)
        });

    // add current location of user to location input and map
    var currentLocationCheckbox = $('#order_by_location_current_loc');
    currentLocationCheckbox.on('click', function () {
        if (currentLocationCheckbox.is(':checked')) {
            if (!(window.currentUserLocation)) {
                initCurrentUserLocation();
            }
            var address = window.currentUserLocation.formatted_address;
            extendedLocInput.val(address);
            extendedLocInput.trigger('geocode');
            submitBtn.removeClass('disabled');
            radiusInput.prop('disabled', false)
        } else {
            submitBtn.addClass('disabled');
            radiusInput.prop('disabled', true);
            extendedLocInput.val('');
        }
    });

    // add location info to orderByData when user has clicked submit btn
    var locDetails = $('#order_by_location_extended_details');
    submitBtn.on('click', function () {
        if (chipsContainer.find('input[name="city_loc"]')){
            chipsContainer
                .find('input[name="city_loc"]')
                .closest('.search-chip')
                .remove();
        }

        addChip(
            'Proximity to ' + extendedLocInput.val(),
            'lat_lng',
            locDetails.find('input[name="lat"]').val() + ',' +
                locDetails.find('input[name="lng"]').val()
        );
        if (radiusInput.val()){
            addChip(
                'Radius ' + radiusInput.val() + ' km',
                'radius',
                radiusInput.val())
        }
        modal.closeModal()
    });

    // set location sorting elements which were previously added by user
    if (args.city_loc){
        var location = args.city_loc.split(',');
        if (location.length == 2){
            cityInput.val(location[0] + ', ' + location[1]);
        }
    } else if (args.lat_lng) {
        var lat_lng = args.lat_lng.split(',');
        if (lat_lng.length == 2) {
            getLocByLatLng(
                lat_lng[0],
                lat_lng[1],
                function (data) {
                    extendedLocInput.val(data.formatted_address);
                    extendedLocInput.trigger('geocode');
                    submitBtn.removeClass('disabled');
                    radiusInput.prop('disabled', false);

                    if (args.radius) {
                        radiusInput
                            .val(args.radius)
                            .closest('.input-field')
                            .find('label')
                            .addClass('active');
                        circle.setRadius(args.radius * 1000);
                        circle.setVisible(true);
                    }
                }
            );
        }
    }

    // open map modal
    openMapModalBtn.on('click', function () {
        modal.openModal();
        google.maps.event.trigger(orderingSearchLocObj.map, "resize")
    });
}

function initOrderByExperience(choices, args){
    var slider = $('#order_by_experience_slider');

    slider.ionRangeSlider({
        type: 'double',
        values: choices.map(function (i) { return i[1] }),
        from: args.exp_from || 0,
        to: args.exp_to || choices.length,
        grid: true,
        onFinish: function(data){
            if (data.from == 0){
                $('input[name="exp_from"]').closest('.search-chip').remove()
            } else {
                addChip(
                    'Experience from ' + data.from_value, 'exp_from', data.from);
            }

            if (data.to == choices.length - 1){
                $('input[name="exp_to"]').closest('.search-chip').remove()
            } else {
                addChip(
                    'Experience to ' + data.to_value, 'exp_to', data.to);
            }
        }
    });
}

function initOrderBySuccess(args){
    var slider = $('#order_by_success_slider');
    slider.ionRangeSlider({
        type: 'double',
        from: args.success_from || 0,
        to: args.success_to || 100,
        postfix: ' %',
        grid: true,
        onFinish: function(data){
            if (data.from == 10){
                $('input[name="success_from"]').closest('.search-chip').remove()
            } else {
                addChip(
                    'Success from ' + data.from + '%', 'success_from', data.from);
            }

            if (data.to == 100){
                $('input[name="success_to"]').closest('.search-chip').remove()
            } else {
                addChip(
                    'Success to ' + data.to + '%', 'success_to', data.to);
            }
        }
    });
}

function redirectWithSortParams(serviceId){
    $('#order_by_submit').on('click', function(){
        var url = '/service/' + serviceId + '?';
        var chipsData = [];
        $('#chips-container').find('.search-chip').each(function() {
            var input = $(this).find('input');
            url += input.attr('name') + '=' + input.val() + '&';
            chipsData.push({
                'chipData': $(this).find('.chip').text(),
                'inputName': input.attr('name'),
                'inputValue': input.val()
            })
        });

        sessionStorage.setItem('searchChipsInfo', JSON.stringify(chipsData));
        window.location = url;
    })
}

function showPreviousChips(args, expTypes){
    // function which sets tags according to request args

    // open accordion tabs
    var triggeredAccordionEl = [];
    function triggerAccordion(el){
        if (_.contains(triggeredAccordionEl, el)){
            return
        } else {
            $(document).ready(function () {
                $('#order-by-' + el + '-accordion-el')
                    .find('.collapsible-header')
                    .trigger('click')
            });
            triggeredAccordionEl.push(el)
        }
    }

    if (args.city_loc) {
        var loc_parts = args.city_loc.split(',');
        if (loc_parts.length == 2) {
            addChip(
                'In ' + loc_parts[0] + ', ' + loc_parts[1],
                'city_loc',
                loc_parts[0] + ',' + loc_parts[1])
        }
        triggerAccordion('location')
    } else if (args.lat_lng){
        var lat_lng = args.lat_lng.split(',');
        if (lat_lng.length == 2){
            getLocByLatLng(
                lat_lng[0],
                lat_lng[1],
                function(data){
                   addChip(
                       'Proximity to ' + data.formatted_address,
                       'lat_lng',
                       args.lat_lng)
                }
            );
            if (args.radius){
                addChip('Radius ' + args.radius + ' km', 'radius', args.radius)
            }
            triggerAccordion('location')
        }
    }

    if (args.exp_from){
        for (i = 0; i < expTypes.length; i++) {
            if (expTypes[i][0] == args.exp_from){
                var expFromStr = expTypes[i][1];
                break
            }
        }
        if (expFromStr) {
            addChip('Experience from ' + expFromStr, 'exp_from', args.exp_from)
            triggerAccordion('experience')
        }
    }

    if (args.exp_to){
        for (i = 0; i < expTypes.length; i++) {
            if (expTypes[i][0] == args.exp_to){
                var expToStr = expTypes[i][1];
                break
            }
        }
        if (expToStr) {
            addChip('Experience to ' + expToStr, 'exp_to', args.exp_to)
            triggerAccordion('experience')
        }
    }

    if (args.success_from && args.success_from <= 100 && args.success_from >= 10){
        addChip(
            'Success from ' + args.success_from + '%',
            'success_from',
            args.success_from);
        triggerAccordion('success')
    }

    if (args.success_to && args.success_to <= 100 && args.success_to >= 10){
        addChip(
            'Success to ' + args.success_to + '%',
            'success_to',
            args.success_to);
        triggerAccordion('success')
    }
}