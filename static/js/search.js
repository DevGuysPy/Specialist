var specialistsCount = null;
var currentPage = null;

function initSearchPage(currentServiceId,
                        expTypes){
    initSpecialistCards(currentServiceId, location.search);

    initOrderByLocation();
    initOrderByExperience(expTypes);
    initOrderBySuccess();
    initOrderSorting();
    redirectWithSortParams(currentServiceId);
    $('#chips-container').on('click', '.material-icons', function(){
        $(this).closest('.search-chip').remove();
        $(this).closest('.chip').tooltip('remove');
    })
}

function initSpecialistCards(serviceId, params){
    var container = $('#specialists-container');
    $('body').removeClass('loaded');
    $.ajax({
        method: 'GET',
        url : '/service/' + serviceId + params,
        success: function(data){
            data = JSON.parse(data);
            specialistsCount = data.specialists_count;
            currentPage = data.current_page;
            container.empty();
            container.prepend($(data.template));
            window.history.pushState("", "", '/service/' + serviceId + params);
            $('#specialists-count').text(
                'Found ' + specialistsCount + ' specialists.');

            var $containerProducts = $("#products").masonry({
                    singleMode: true, isAnimated: true
                });
            $containerProducts.imagesLoaded(function() {
                $containerProducts.masonry({
                    itemSelector: ".product",
                    columnWidth: ".product-sizer"
                });
            });

            specialistCardHandler();
            paginationHandler(serviceId, specialistsCount, currentPage);
        },
        complete: function(){
            setTimeout(function() {
                $('body').addClass('loaded')
            }, 100)
        }
    });
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

    $('.show-description').on('click', function(){
        $(this).hide();
        $(this).parent().find('.hidden-text').show()
    });

    $('.show-phone').on('click', function(){
        $(this).hide();
        $(this).parent().find('.phone').show()
    });
}

function paginationHandler(serviceId, specialistsCount, currentPage) {
    var pagesCount = parseInt(specialistsCount / 12);
    if (specialistsCount - pagesCount * 12 != 0) {
        pagesCount = pagesCount + 1
    }

    var pagination = $('.page-numbers');

    _.forEach(_.range(1, pagesCount + 1), function (pageNum) {
        pagination.append(
            '<li class="waves-effect page-number">' +
            '<a href="#" id="' + pageNum + '">' + pageNum + '</a>' +
            '</li>')
    });

    var pageNumberEl = $('.page-number');

    function makeUrl(pageNum){
        var index = location.search.indexOf('page=');
        var params = null;
        if (index != -1){
            params =
                location.search.substr(0, index + 5) +
                 pageNum +
                location.search.substr(index+ 7, location.search.length)
        } else if (location.search) {
            params = location.search + '&page=' + pageNum
        } else {
            params = '?page=' + pageNum
        }

        return params
    }

    pageNumberEl.on('click', function(){
        initSpecialistCards(serviceId, makeUrl($(this).find('a').attr('id')) )
    });

    if (currentPage > 5){
        pageNumberEl.slice(1, currentPage - 5).hide();
    }
    if (currentPage < pagesCount - 5) {
        pageNumberEl.slice(currentPage + 4, pagesCount - 1).hide();
    }

    var nextEl = $('#next_page');
    var previousEl = $('#previous_page');

    previousEl.on('click', function(){
        initSpecialistCards(serviceId, makeUrl(currentPage - 1) )
    });

    nextEl.on('click', function(){
        initSpecialistCards(serviceId, makeUrl(currentPage + 1) )
    });

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
    var tooltipped = chipData.length > 27 ?
        ' tooltipped" data-position="top" data-delay="50" data-tooltip="' +
        chipData + '"': '"';
    chipData = chipData.length > 27 ? chipData.slice(0, 27) + '...': chipData;

    var chip = $(
        '<div class="search-chip">' +
        '<div class="chip' + tooltipped + '>' +
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
    );

    $('.chip.tooltipped').tooltip({delay: 50});

    return chip
}

function initOrderByLocation(){
    var modal = $('#map-modal');
    var cityInput = $('#order_by_location_city_autocomplete');
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
        chipsContainer
            .find('input[name="lat_lng"], ' +
            'input[name="radius"], ' +
            'input[name="sort_by"][value="5"], ' +
            'input[name="sort_by"][value="6"]').each(function(){
                $(this)
                    .closest('.search-chip')
                    .remove();
            });

        var city = cityDetails.find('input[name="locality"]').val();
        var country = cityDetails.find('input[name="country"]').val();
        addChip(
            'In ' + city + ', ' + country,
            'city_loc',
            city + ',' + country
        ).find('.material-icons').on('click', function(){
                cityInput.val('')
            });
    });
}

function initOrderByExperience(choices){
    var slider = $('#order_by_experience_slider');

    slider.ionRangeSlider({
        type: 'double',
        values: choices.map(function (i) { return i[1] }),
        from: 0,
        to: choices.length,
        grid: true,
        onFinish: function(data){
            if (data.from == 0){
                $('input[name="exp_from"]').closest('.search-chip').remove()
            } else {
                addChip(
                    'Experience from ' + data.from_value,
                    'exp_from',
                    data.from
                ).find('.material-icons').on('click', function(){
                        slider.data("ionRangeSlider").update({
                            from: 0
                        });
                    });
            }

            if (data.to == choices.length - 1){
                $('input[name="exp_to"]').closest('.search-chip').remove()
            } else {
                addChip(
                    'Experience to ' + data.to_value,
                    'exp_to',
                    data.to
                ).find('.material-icons').on('click', function(){
                        slider.data("ionRangeSlider").update({
                            to: choices.length - 1
                        });
                    });
            }
        }
    });
}

function initOrderBySuccess(){
    var slider = $('#order_by_success_slider');
    slider.ionRangeSlider({
        type: 'double',
        from: 0,
        to: 100,
        postfix: ' %',
        grid: true,
        step: 5,
        onFinish: function(data){
            if (data.from == 10){
                $('input[name="success_from"]')
                    .closest('.search-chip')
                    .remove()
            } else {
                addChip(
                    'Success from ' + data.from + '%',
                    'success_from',
                    data.from
                ).find('.material-icons').on('click', function(){
                        slider.data("ionRangeSlider").update({
                            from: 10
                        });
                    });
            }

            if (data.to == 100){
                $('input[name="success_to"]')
                    .closest('.search-chip')
                    .remove()
            } else {
                addChip(
                    'Success to ' + data.to + '%',
                    'success_to',
                    data.to
                ).find('.material-icons').on('click', function(){
                        slider.data("ionRangeSlider").update({
                            to: 100
                        });
                    });
            }
        }
    });
}

function initOrderSorting(){
    var btns = $('input[name="sorting-radio"][class="common-sorting"]');
    btns.on('click', function(){
        var input = $('input[name="sorting-radio"]:checked');
        var label = $('label[for="' + input.attr('id') + '"]');
        addChip(
            label.text(),
            'sort_by',
            input.attr('id').replace('sorting-radio-', '')
        ).find('.material-icons').on('click', function(){
                input.prop('checked', false)
            });
    });

    var modal = $('#map-modal');
    var locRadio = $('#sorting-radio-5, #sorting-radio-6');

    locRadio.one('click', function(e){
        e.preventDefault();

        var radio = $(this);
        var label = $('label[for="' + radio.attr('id') + '"]');

        var extendedLocInput = $('#order_by_location_autocomplete');
        var submitBtn = $('#order_by_location_submit');
        var radiusInput = $('#order_by_location_radius');
        var chipsContainer = $('#chips-container');


        // init extended location autocomplete and map
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
            location: [49.337407, 29.8229751]
        }).bind("geocode:dragged", function (event, latLng) {
            getLocByLatLng(
                latLng.lat(),
                latLng.lng(),
                function (address) {
                    // add position of marker to location input when marker
                    // is moved
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
            visible: false
        });
        circle.bindTo('center', orderingSearchLocObj.marker, 'position');
        google.maps.event.addListener(circle, 'dragend', function () {
            var center = circle.getCenter();
            getLocByLatLng(
                center.lat(),
                center.lng(),
                function (address) {
                    // add position of marker to location input when circle
                    // is moved
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
                '',
                'lat_lng',
                locDetails.find('input[name="lat"]').val() + ',' +
                    locDetails.find('input[name="lng"]').val()
            ).hide();

            addChip(
                label.text() + ' to ' + extendedLocInput.val(),
                'sort_by',
                radio.attr('id').replace('sorting-radio-', '')
            ).find('.material-icons').on('click', function(){
                    radio.prop('checked', false)
                });

            radio.prop('checked', true);
            if (radiusInput.val()){
                addChip(
                    'Radius ' + radiusInput.val() + ' km',
                    'radius',
                    radiusInput.val())
            }
            modal.closeModal()
        });
    });

    locRadio.on('click', function(e){
        e.preventDefault();

        // open map modal
        $('#map-modal').openModal();
        google.maps.event.trigger(orderingSearchLocObj.map, "resize")
    });
}

function redirectWithSortParams(serviceId){
    $('#order_by_submit').on('click', function(){
        var params = '?';
        $('#chips-container').find('.search-chip').each(function() {
            var input = $(this).find('input');
            params += input.attr('name') + '=' + input.val() + '&';
        });

        initSpecialistCards(serviceId, params)
    })
}