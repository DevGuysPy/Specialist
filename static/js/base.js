$('select').material_select();
$('.tooltipped').tooltip({delay: 50});

var socket = io.connect('http://' + document.domain + ':' + location.port);

$(document).ready(function() {
    initCurrentUserLocation();
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
        var btn = $(this);
        var preloader = initPreloader(btn);
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
                        'full_name' in data.errors ? data.errors.full_name : '');
                    preloader.hide();
                    btn.show()
                }
            },
            error: function(a, error){
                signPasswordErrorEl.text('Ups, something go wrong.');
                preloader.hide();
                $(this).show();
                console.log(error)
            }

        })
    });

    var loginEmailErrorEl = $('.error.login-email');
    var loginPasswordErrorEl = $('.error.login-password');
    $('#login_submit').on('click', function(){
        var btn = $(this);
        var preloader = initPreloader(btn);
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
                    preloader.hide();
                    btn.show();
                }
            },
            error: function(a, error){
                loginPasswordErrorEl.text('Ups, something go wrong.');
                preloader.hide();
                $(this).show();
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
    if (window.currentUserLocation){
        return
    }
    navigator.geolocation.getCurrentPosition(function (position) {
        getLocByLatLng(
            position.coords.latitude,
            position.coords.longitude,
            function(data){
                window.currentUserLocation = data;
                $.ajax({
                    method: 'POST',
                    url: '/set_current_location',
                    data: JSON.stringify(data),
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
            successFunc(_.head(data.results))
        }
    })
}

function initPreloader(btn){
    var main_preloader = $('#main-preloader');
    btn.hide();
    var previous_prl = btn.parent().find('.preloader-wrapper');

    var custom_preloader = null;
    if (!(previous_prl.length)) {
        custom_preloader = main_preloader
            .clone()
            .insertBefore(btn)
            .show();
        custom_preloader.removeAttr('id');
    } else {
        custom_preloader = previous_prl.show();
    }

    return custom_preloader
}

function setMarkers(map, markers) {
  for (var i = 0; i < markers.length; i++) {
    markers[i].setMap(map);
  }
}

function isEmpty(obj) {
    for(var prop in obj) {
        if(obj.hasOwnProperty(prop))
            return false;
    }

    return true;
}

if(typeof(String.prototype.trim) === "undefined") {
    String.prototype.trim = function() {
        return String(this).replace(/^\s+|\s+$/g, '');
    };
}