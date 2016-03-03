$(document).ready(function() {
    $('select').material_select();
    navigator.geolocation.getCurrentPosition(function(position){
        var data = {
            'latitude': position.coords.latitude,
            'longitude': position.coords.longitude
        };
        $.ajax({
            method: 'POST',
            url: '/set_current_location',
            data: JSON.stringify(data),
            contentType: "application/json"
        }).done(function (data) {
        })
    });
    $('.tooltipped').tooltip({delay: 50});
    $('ul.tabs').tabs();
    var infoCardSettings = $('#info-card-tab');
    infoCardSettings.find('a').removeClass('active');
    infoCardSettings.click();
    infoCardSettings.find('a').addClass('active')

});

function initInputAutocomplete(input, apiUrl, params, onSelectFunc){
    input.autocomplete({
        serviceUrl: apiUrl,
        params: params,
        onSelect: function (suggestion) {
            onSelectFunc(suggestion);
        }
    })
}
