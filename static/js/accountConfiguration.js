function initAccountSettings(change_password_url, set_phone_url) {
    checkPasswordFields();
    phoneFieldEmpty();
    deletePhone();
    changeInfo();
    displayAvatar();
    settingsCardShow();
    //click events for forms' submits
    $('#change-password-submit').click(function(event){
        event.preventDefault();
        $('#cd-popup-pass').addClass('is-visible');
        $('#accept-pass').click(function(){
            adjustSettings(change_password_url, $('#change_password_form'), $('.change_password_error'))
        });
    });

    $('#set-phone-submit').click(function(event){
        event.preventDefault();
        adjustSettings(set_phone_url, $('#set_phone_form'), $('.set_phone_error'))
    });
    $('#set_number').mask('+38(000)000-0000')

}
function settingsCardShow(){
    var left, opacity, right ; //card properties which we will animate
    var animating; //flag to prevent quick multi-click glitches
    var infoCard = $("#info-card");
    var contactsCard = $("#contacts-card");
    var passwordCard = $("#password-card");

    $("#info-card-tab").click(function(){
        if(animating) return false;
        animating = true;

        contactsCard.css('display', 'none');
        passwordCard.css('display', 'none');
        infoCard.css('opacity', '0');

        infoCard.animate({
            opacity: 1
        }, {
            step: function(now, mx) {
                right = ((1-now) * 50)+"%";
                $(this).css({'right': right, 'opacity':opacity, 'display':'block'});
            },
            duration: 650,
            complete: function(){
                $("#info-card").show();
                animating = false;
            },
            //this comes from the custom easing plugin
            easing: 'easeInOutBack'
        });
    });

    $("#contacts-card-tab").click(function(){
        if(animating) return false;
        animating = true;

        infoCard.css('display', 'none');
        passwordCard.css('display', 'none');
        contactsCard.css('opacity', '0');

        contactsCard.animate({
            opacity: 1
        }, {
            step: function(now, mx) {
                left = ((1-now) * 50)+"%";
                $(this).css({'left': left, 'opacity':opacity, 'display':'block'});
            },
            duration: 650,
            complete: function(){
                $("#contacts-card").show();
                animating = false;
            },
            //this comes from the custom easing plugin
            easing: 'easeInOutBack'
        });
    });
    $("#password-card-tab").click(function(){
        if(animating) return false;
        animating = true;
        infoCard.css('display', 'none');
        contactsCard.css('display', 'none');
        passwordCard.css('opacity', '0');

        passwordCard.animate({
            opacity: 1
        }, {
            step: function(now, mx) {
                right = ((1-now) * 50)+"%";
                $(this).css({'right': right, 'opacity':opacity,'display':'block'});
            },
            duration: 650,
            complete: function(){
                $("#password-card").show();
                animating = false;
            },
            //this comes from the custom easing plugin
            easing: 'easeInOutBack'
        });
    });
}
function displayAvatar(){
    var fileInput = $('#photo-file-input');

    var maxPhotoSize = 2 * 1024 * 1024;

    fileInput.change(function () {
        var photoFile = this.files[0];
        var photoSize = photoFile.size;
        if(photoSize > maxPhotoSize){
            $('#error_photo_error').html('File size is over 2 MB')
        }else{
            readImageURL(this);
        }
    });

}
function readImageURL(input) {

    if (input.files) {
        var reader = new FileReader();

        reader.onload = function (e) {
            var avatar = $('#avatar');
            var photoPreLoader = $('#photo-preloader');
            avatar.attr('src', e.target.result);
            photoPreLoader.removeClass('active')
        };
        reader.onprogress = function(e){
            var photoPreLoader = $('#photo-preloader');
            photoPreLoader.addClass('active')
        };

        reader.readAsDataURL(input.files[0]);
    }
}



function changeInfo() {
    //click submit
    $("#edit_profile_form").submit(function (event) {
        event.preventDefault();
        $('#cd-popup-info-edit').addClass('is-visible');
        $('#accept-info-edit').click(function(){
            var data = new FormData($('#edit_profile_form')[0]);
            $.ajax({
                method: 'POST',
                url: '/account/settings/edit/profile',
                data: data,
                cache: false,
                contentType: false,
                processData: false
            }).done(function (response) {
                if (response.status == 'ok') {
                    location.reload();
                } else {
                    _.forEach(response.input_errors, function (value, key) {
                        var errorInput = $('#' + key);
                        var errorDiv = $('#error_' + key);
                        errorDiv.html(value);
                        errorInput.attr('class', 'invalid');
                    });
                }
            })
        });
    });

}

//press on X or ESCAPE to remove pop-up
function removePopUp() {

    $(document).on('keyup', function(event){
        if(event.which=='27'){
            $('.cd-popup').removeClass('is-visible');
        }
    });
    $('.cd-popup').on('click', function(event){
        $(this).removeClass('is-visible');
    });
}

function deletePhone(){

    var initButton = $('#delete');
    initButton.addClass('disabled');
    var checkBox = $(':checkbox[name="phone"]');

    //enabling delete button
    //if one checkbox is checked at least ==> remove disable style
    checkBox.click(function(){
        if ($('#phone1').is(':checked') || $('#phone2').is(':checked') ) {
            initButton.removeClass('disabled');
        }else{
            initButton.addClass('disabled');
        }
    });
    removePopUp();

    initButton.click(function(){
        var phonesToDelete = [];
        var checkedBoxes = $("input:checkbox[name=phone]:checked");
        checkedBoxes.each(function(){
            phonesToDelete.push(this.value)
        });

        $('#cd-popup-contacts').addClass('is-visible');

        $('#accept-contacts').click(function(){
            $.ajax({
                method: 'POST',
                url: '/account/delete/phone',
                data: JSON.stringify(phonesToDelete),
                dataType: "json",
                contentType: "application/json"
            }).done(function (response) {
                if (response.status == 'ok') {
                    location.reload();
                }else{
                    alert('Removing the disabled class is not a good idea')
                }
            });
        });
    });
}

function phoneFieldEmpty() {

    var setPhoneError = $('.set_phone_error');

    var setReservePhoneError = $('.set_reserve_phone_error');

    //'onkeyup' events for phone fields
    $('#set_number').on('keyup', function () {
        setPhoneError.empty();
    });
    $('#set_reserve_number').on('keyup', function () {
        setReservePhoneError.empty();
    });
}

function adjustSettings(url, data, errorField) {
    errorField.empty();
    $.ajax({
        method: 'POST',
        url: url,
        data: data.serializeArray()
    }).done(function (response) {
        if (response.status == 'ok') {
            location.reload();
        } else {
            _.forEach(response.input_errors, function (value, key) {
                var errorInput = $('#' + key);
                var errorDiv = $('#error_' + key);
                errorDiv.html(value[0]);
                errorInput.attr('class', 'invalid');
            });
        }
    })
}

function checkPasswordFields(){
    var currentPasswordInput = $('#current_password');
    var currentPasswordErrorDiv = $('#error_current_password');

    var newPasswordErrorDiv = $('#error_new_password');
    var newPasswordAgainErrorDiv = $('#error_new_password_again');

    var passwordInput = $('#new_password');
    var passwordAgainInput = $('#new_password_again');

    function emptyNewPasswordErrorDiv(){
        newPasswordErrorDiv.empty();
        newPasswordAgainErrorDiv.empty();
    }
    function markValid(){
        passwordInput.removeAttr('class', 'invalid');
        passwordAgainInput.removeAttr('class', 'invalid');
    }

    function markInvalid(){
        passwordInput.attr('class', 'invalid');
        passwordAgainInput.attr('class', 'invalid');

    }

    function raiseErrorMessage(){
        newPasswordErrorDiv.html('Password does not match');
        newPasswordAgainErrorDiv.html('Password does not match');
    }

    currentPasswordInput.on('keyup', function() {
        currentPasswordErrorDiv.empty();
        $(this).removeAttr('class', 'invalid');
    });

    passwordInput.on('keyup', function() {

        if(passwordInput.val() == passwordAgainInput.val()
            && passwordInput.val().length
            >= 8 && passwordInput.val().length <= 64){
            emptyNewPasswordErrorDiv();
            markValid();
        }
        if(passwordInput.val() != passwordAgainInput.val()){
            emptyNewPasswordErrorDiv();
            markInvalid();
            raiseErrorMessage();
        }
        if(passwordInput.val().length < 8 || passwordInput.val().length > 64){
            emptyNewPasswordErrorDiv();
            markInvalid();
            newPasswordErrorDiv.html('Field must be between 8 and 64 characters long');

        }
    });

    passwordAgainInput.on('keyup', function() {

        if(passwordInput.val() == passwordAgainInput.val()
            && passwordAgainInput.val().length >= 8
            && passwordAgainInput.val().length <= 64){
            emptyNewPasswordErrorDiv();
            markValid();
        }
        if(passwordInput.val() != passwordAgainInput.val()){
            emptyNewPasswordErrorDiv();
            markInvalid();
            raiseErrorMessage();

        }
        if(passwordAgainInput.val().length < 8
            || passwordAgainInput.val().length > 64){
            emptyNewPasswordErrorDiv();
            passwordAgainInput.attr('class', 'invalid');
            newPasswordAgainErrorDiv.html('Field must be between 8 and 64 characters long');
        }
    });
}