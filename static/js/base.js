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
$(".translation-button").dropdown({
        inDuration: 300,
        outDuration: 225,
        constrain_width: !1,
        hover: !0,
        gutter: 0,
        belowOrigin: !0,
        alignment: "left"
});
function changeLanguage(langCode) {
    $.ajax({
        method: 'POST',
        url: '/change/' + langCode
    }).done(function (data) {
        if (data.status == 'ok') {
            window.location.reload()
        }
        else {
            Materialize.toast('<span>Fuck off. ©Ura Muraviov</span>', 3000);
        }
    });
}
