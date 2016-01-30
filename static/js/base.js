$(document).ready(function() {
    $('select').material_select();
    initCurrentUserLocation();
    $('.tooltipped').tooltip({delay: 50});

    $('.sign_up_or_login').on('click', function(){
        var modal = $('#sign-up-or-login-modal');
        modal.openModal();
        initSignUpOrLogin(modal)
    });
});

function initSignUpOrLogin(modal){
    var signEmailErrorEl = $('.error.sign-up-email');
    var signFullNameErrorEl = $('.error.sign-up-full_name');
    var signPasswordErrorEl = $('.error.sign-up-password');

    $('#sign_up_submit').on('click', function(){
        $.ajax({
            url: '/user_sign_up?login=true',
            method: 'POST',
            data: $('#sign_up_form_modal').serializeArray(),
            success: function(data){
                if (data.status != 'error') {
                    modal.closeModal();
                    $('.login-event').trigger('login')
                } else {
                    signEmailErrorEl.text(
                        'email' in data.errors ? data.errors.email : '');
                    signPasswordErrorEl.text(
                        'password' in data.errors ? data.errors.password : '');
                    signFullNameErrorEl.text(
                        'full_name' in data.errors ? data.errors.full_name : '')
                }
            },
            error: function(a, error){
                console.log(error)
            }

        })
    });

    var loginEmailErrorEl = $('.error.login-email');
    var loginPasswordErrorEl = $('.error.login-password');
    $('#login_submit').on('click', function(){
        $.ajax({
            url: '/login',
            method: 'POST',
            data: $('#login_form_modal').serializeArray(),
            success: function(data){
                if (data.status != 'error') {
                    modal.closeModal();
                    $('.login-event').trigger('login')
                } else {
                    loginEmailErrorEl.text(
                        'email' in data.errors ? data.errors.email : '');
                    loginPasswordErrorEl.text(
                        'password' in data.errors ? data.errors.password : '');
                }
            },
            error: function(a, error){
                console.log(error)
            }
        })
    });
}

function initInputAutocomplete(input, apiUrl, params, onSelectFunc){
    input.autocomplete({
        serviceUrl: apiUrl,
        params: params,
        onSelect: function (suggestion) {
            onSelectFunc(suggestion);
        }
    })
}

function initCurrentUserLocation() {
    navigator.geolocation.getCurrentPosition(function (position) {
        getLocByLatLng(
            position.coords.latitude,
            position.coords.longitude,
            function(data){
                var locData = _.head(data.results);
                window.currentUserLocation = locData;
                $.ajax({
                    method: 'POST',
                    url: '/set_current_location',
                    data: JSON.stringify(locData),
                    contentType: "application/json"
                });
        });
    });
}

function getLocByLatLng(lat, lng, successFunc) {
    $.ajax({
        url: 'http://maps.googleapis.com/maps/api/geocode/json?latlng=' +
        lat + ',' + lng + '&sensor=true',
        success: function(data){
            successFunc(data)
        }
    })
}
