var $containerProducts = $(".prepend").masonry({
    singleMode: true
});
$containerProducts.imagesLoaded(function() {
    $containerProducts.masonry({
        itemSelector: ".product",
        columnWidth: ".product-sizer",
        isAnimated: true
    });
});
var letters = ['#d32f2f', '#c2185b', '#7b1fa2', '#512da8', '#303f9f', '#1976d2', '#0288d1', '#0097a7', '#00796b', '#388e3c', '#689f38', '#afb42b', '#fbc02d', '#ffa000', '#f57c00', '#e64a19', '#5d4037', '#616161', '#455a64'];
$('.random-bg').each(function() {
    var color = letters[Math.floor(Math.random() * letters.length)];
    $( this ).css("background-color", color);
});

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
                    addServiceCard(item)
                });
                toggleAddSelectedServicesBtn();
            }
        });
    });
}

function addServiceCard(service){
    $('.specialist-services').show();
    $(".no-services-services").hide();
    var $serviceEl = $('<div class="product">' +
        '<div class="card new-service" id="card-stats">' +
        '<div class="card-content white-text front">' +
        '<h3 class="card-stats-title">' +
        service.name  +
        '</h3>' +
        '</div></div>' +
        '</div>');
    $containerProducts.prepend( $serviceEl ).masonry('prepended', $serviceEl);
    $('.new-service').each(function() {
        var color = letters[Math.floor(Math.random() * letters.length)];
        $( this ).css("background-color", color);
    });

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

function removeService(service_id){
    $.ajax({
        method: 'POST',
        url: '/remove_services/' + service_id,
        contentType: "application/json"
    });
    $containerProducts.masonry( 'remove', $containerProducts.find('#service_' + service_id) ).masonry('layout');
}
