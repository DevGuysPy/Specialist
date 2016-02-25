var specialistsCount = null;
var currentPage = null;

function initSearchPage(currentServiceId,
                        expTypes){
    var showOnMapMap = initShowOnMapModal(currentServiceId);

    // reload specialist cards when user clicks back button
    window.onpopstate = function(event) {
        var paramsStr = '';
        if (!(isEmpty(event.state))) {
            paramsStr = '?';
            for (var key in event.state) {
                if (key) {
                    paramsStr += key + '=' + event.state[key]
                }
            }
        }

        initSpecialistCards(
            currentServiceId,
            paramsStr,
            true,
            showOnMapMap,
            false)
    };

    initSpecialistCards(currentServiceId, location.search, true, showOnMapMap);

    initOrderByLocation();
    initOrderByExperience(expTypes);
    initOrderBySuccess();
    initOrderSorting();

    // handle search chips deletion
    var chipsContainer = $('#chips-container');
    chipsContainer.on('click', '.material-icons', function(){
        chipsContainer = $('#chips-container');

        $(this).closest('.search-chip').remove();
        $(this).closest('.chip').tooltip('remove');

        if (!(chipsContainer.find('.search-chip').length)){
            chipsContainer.find('#delete-filters').remove()
        }
    });

    // handle delete all filters btn
    $('#delete-filters-div').on('click', '#delete-filters', function(){
        $(this).tooltip('remove');
        $(this).remove();
        chipsContainer.find('.search-chip').remove();
        redirectWithSortParams(currentServiceId, showOnMapMap)
    });

    var showFilters = $('#show-search-filters-btn');
    var hideFilters = $('#hide-search-filters-btn');
    var submitBtn = $('#order_by_submit');

    submitBtn.on('click', function() {
        redirectWithSortParams(currentServiceId, showOnMapMap)
    });

    showFilters.on('click', function(){
        $( ".search-filter").parent().first().show( "fast", function showNext() {
            $( this ).next().show( "fast", showNext );
        });
        showFilters.hide();
        hideFilters.show();
        submitBtn.closest('.col').show()
    });

    hideFilters.on('click', function(){
        $( ".search-filter").parent().hide( 1000 );
        showFilters.show();
        hideFilters.hide();
        submitBtn.closest('.col').hide()
    })


}

function initSpecialistCards(serviceId, params, anim, map, pushState){
    // make ajax call from which we receive information about specialists
    // according o params.
    // With this information will be initialized specialist cards

    var container = $('#specialists-container');
    if (anim){
       $('body').removeClass('loaded');
    }
    $.ajax({
        method: 'GET',
        url : '/service/' + serviceId + params,
        cache: false,
        success: function(data){
            data = JSON.parse(data);
            specialistsCount = data.specialists_count;
            currentPage = data.current_page;
            container.empty();
            container.prepend(data.template);

            if (typeof (pushState) == 'undefined' || pushState) {
                var paramsSliced = params.slice(1, params.length).split('&');

                var paramsDict = {};
                for (i = 0; i < paramsSliced.length; i++) {
                    var parts = paramsSliced[i].split('=');
                    paramsDict[parts[0]] = parts[1]
                }
                window.history.pushState(paramsDict, "", '/service/' + serviceId + params);
            }
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

            if (typeof (map) != 'undefined'){
                $('#show-on-map-modal-btn')
                    .off('click')
                    .one('click', function(){
                        addShowOnMapModalMarkers(data.specialists_for_map, map)
                    });
            }


            specialistCardHandler();
            paginationHandler(serviceId, specialistsCount, currentPage, map);
            if (anim) {
                $('body').addClass('loaded')
            }
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

function paginationHandler(serviceId, specialistsCount, currentPage, map) {
    // handle pagination for specialist cards

    var pagesCount = parseInt(specialistsCount / 12);
    if (specialistsCount - pagesCount * 12 != 0) {
        pagesCount = pagesCount + 1
    }

    var pagination = $('.page-numbers');

    _.forEach(_.range(1, pagesCount + 1), function (pageNum) {
        pagination.append(
            '<li class="waves-effect page-number">' +
            '<a href="javascript:void(0)" id="' + pageNum + '">' + pageNum + '</a>' +
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
                location.search.substr(index + 8, location.search.length)
        } else if (location.search) {
            params = location.search + '&page=' + pageNum
        } else {
            params = '?page=' + pageNum
        }

        return params
    }

    pageNumberEl.on('click', function(){
        initSpecialistCards(
            serviceId,
            makeUrl($(this).find('a').attr('id')),
            true,
            map)
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
        initSpecialistCards(serviceId, makeUrl(currentPage - 1), true, map)
    });

    nextEl.on('click', function(){
        initSpecialistCards(serviceId, makeUrl(currentPage + 1), true, map )
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

    var deleteFilters = $('#delete-filters-div');
    if (!(deleteFilters.find('#delete-filters').length)){
        var btn =
            $('<a id="delete-filters" class="round-btn btn-floating ' +
                    'btn-large waves-effect waves-light blue-grey darken-3 ' +
                    'tooltipped" data-position="top" data-delay="50" ' +
                    'data-tooltip="Delete filters" style="margin-left: 20px;">' +
                '<i class="material-icons">delete</i>' +
            '</a>');
        deleteFilters.append(btn);
        btn.tooltip()
    }

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
        setGlobal: 'orderingSearchCity',
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

    $('#by-location-tab-trigger').on('click', function(){
        google.maps.event.trigger(orderingSearchCityLocObj.map, "resize")
    })
}

var markers = [];
var openSpecInfoWindow = null;
function initShowOnMapModal(currentServiceId){
    var modal = $('#show-on-map-modal');

    var map = new google.maps.Map(document.getElementById('show-on-map-map'), {
        center: {lat: 72, lng: -90},
        zoom: 3
    });


    var spec_info = [];
    var infoWindow = new google.maps.InfoWindow({content: 'bla', maxWidth: 400});
    openSpecInfoWindow = function openInfo(el) {
        function initServicesStr(services) {

            services.splice(
                _.findIndex(services, {'id': currentServiceId}), 1);
            var sliced = services.slice(0, 3);

            var str = 'Also offers ';
            for (i = 0; i < sliced.length; i++) {
                var comma = i == sliced.length - 1 ? '' : ', ';
                str += '<a href="/service/' + sliced[i].id + '">' +
                    sliced[i].title + '</a>' + comma;
            }

            if (services.length > 3) {
                str += ' and ' + (services.length - 3) + ' more.'
            } else {
                str += '.'
            }

            return str
        }

        function addWindow(spec) {
            var org = typeof (spec.org_id) != 'undefined' ?
                'Works in <a href="/company/' +
                spec.org_id + '/profile">' + spec.org.name + '</a>' :
                'Doesn`t work in company';
            var services = spec.services.length != 1 ?
                initServicesStr(spec.services) :
                'Doesn`t offer any other services.';
            var info =
                '<div class="row map-spec-card no-margin">' +
                '<div class="col m12 no-padding center">' +
                '<a href="/account/' + spec.user.id + '">' +
                '<img src="/static/img/profile.png" alt="U" ' +
                'class="left img circle responsive-img valign profile-image">' +
                '</a>' +
                '<a href="/account/' + spec.user.id + '">' +
                '<p class="title">' + spec.user.first_name + ' ' +
                    spec.user.last_name + '</p>' +
                '</a>' +
                '</div>' +
                '</div>' +
                '<div class="row">' +
                '<div class="col m12">' +
                '<i class="material-icons tiny"style="display: ' +
                'inline;">location_on</i><p style="display: ' +
                'inline; margin: 5px 0 0 5px;">' + spec.location + '</p>' +
                '</div>' +
                '<div class="divider" style="width: 99%;"></div>' +
                '<div class="col m12">' +
                '<i class="material-icons tiny"style="display: ' +
                'inline;">build</i><p style="display: ' +
                'inline; margin: 5px 0 0 5px;">Experience: ' + spec.experience.value + '</p>' +
                '</div>' +
                '<div class="divider" style="width: 99%;"></div>' +
                '<div class="col m12">' +
                '<i class="material-icons tiny" style="display: ' +
                'inline;">account_balance</i><p style="display: ' +
                'inline; margin: 5px 0 0 5px;">' + org + '</p>' +
                '</div>' +
                '<div class="divider" style="width: 99%;"></div>' +
                '<div class="col m12">' +
                '<i class="material-icons tiny" style="display: ' +
                'inline;">work</i><p style="display: inline; margin: ' +
                '5px 0 0 5px;">' + services + '</p>' +
                '</div>' +
                '<div class="divider" style="width: 99%;"></div>' +
                '<div class="col m12">' +
                '<p class="center no-margin">Success jobs: 70%</p>' +
                '<div class="progress">' +
                '<div class="determinate" style="width: 70%"></div>' +
                '</div>' +
                '</div>' +
                '<div class="col m12">' +
                '<a href="/account/' + spec.user.id + '">' +
                '<p class="right no-margin" style="font-size: 17px;">More &raquo;</p>' +
                '</a>' +
                '</div>' +
                '</div>';
            infoWindow.setContent(info);
            infoWindow.open(map, el);

        }

        var spec = _.find(spec_info, {id: el.labelContent});
        if (typeof (spec) == 'undefined') {
            var filters = [
                {
                    "name": "user_id",
                    "op": "==",
                    "val": el.labelContent
                }
            ];
            $.ajax({
                data: {"q": JSON.stringify({"filters": filters})},
                dataType: "json",
                url: '/api/specialist',
                contentType: "application/json",
                success: function (data) {
                    var spec = _.head(data.objects);
                    if (!(spec)) {
                        return
                    }
                    spec_info.push({
                        id: el.labelContent,
                        data: spec
                    });
                    addWindow(spec)
                }
            })
        } else {
            addWindow(spec.data)
        }

    };

    return map;
}

function addShowOnMapModalMarkers(specialists, map){
    if (markers.length){
        setMarkers(null, markers)
    }

    for (i = 0; i < specialists.length; i++) {
        var item = specialists[i];
        var m = new MarkerWithLabel({
            position: {'lat': parseFloat(item.lat), 'lng': parseFloat(item.lng)},
            map: map,
            labelContent: item.user_id,
            labelClass: "labels" // the CSS class for the label
         });
        markers.push(m);
        m.addListener("click", function (e) { openSpecInfoWindow(this) });

    }

    var modal = $('#show-on-map-modal');
    $('#show-on-map-modal-btn').on('click', function(){
        modal.openModal();
        google.maps.event.trigger(map, "resize");
    });

    modal.openModal();
    google.maps.event.trigger(map, "resize");
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

    var sortingFilter =  $('#sorting-filter');
    var mapInit = false;
    var mapOption = null;
    sortingFilter.find('select').change(function(e, init){
        if (typeof (init) != 'undefined') {
            return null
        }

        var selectedOption = $(this).find('option:selected');
        if (_.contains(
                [5, 6], parseInt(selectedOption.val()))){
            mapOption = selectedOption;
            if (!(mapInit)){
                initMap();
            }
            $('#map-modal').openModal();
            google.maps.event.trigger(orderingSearchLocObj.map, "resize")
        } else {
            addChip(
                selectedOption.text(),
                'sort_by',
                selectedOption.val()
            );
        }
    });

    function initMap(){
        mapInit = true;

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
                mapOption.text() + ' to ' + extendedLocInput.val(),
                'sort_by',
                mapOption.val()
            );

            if (radiusInput.val()){
                addChip(
                    'Radius ' + radiusInput.val() + ' km',
                    'radius',
                    radiusInput.val())
            }
            modal.closeModal()
        });
    }
}

function redirectWithSortParams(serviceId, map){
    var params = '?';
    $('#chips-container').find('.search-chip').each(function() {
        var input = $(this).find('input');
        params += input.attr('name') + '=' + input.val() + '&';
    });

    initSpecialistCards(serviceId, params, true, map)
}