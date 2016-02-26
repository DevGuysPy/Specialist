function initSpecCreation(createSpecialistURL,
                          categoryApiURL,
                          serviceApiURL){
    createSpecialist(createSpecialistURL);
    initLocationAutocomplete();
    addValidationHandlers();
    initInputAutocomplete(
        $('#category_selector'),
        categoryApiURL,
        {},
        function (suggestion) {
            $('#service_selector').prop('disabled', false);
            $('#category_selector')
                .removeClass('invalid')
                .addClass('valid');
            initServiceSelector(suggestion.data, serviceApiURL)
        });
}

function createSpecialist(URL){
    var current_fs, next_fs, previous_fs; //fieldsets
    var left, opacity, scale; //fieldset properties which we will animate
    var animating; //flag to prevent quick multi-click glitches

    $(".next").click(function(){
        if(animating) return false;
        animating = true;

        current_fs = $(this).parent();
        next_fs = $(this).parent().next();

        //activate next step on progressbar using the index of next_fs
        $("#progressbar li").eq($("fieldset").index(next_fs)).addClass("active");

        //show the next fieldset
        next_fs.show();
        //hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now, mx) {
                //as the opacity of current_fs reduces to 0 - stored in "now"
                //1. scale current_fs down to 80%
                scale = 1 - (1 - now) * 0.2;
                //2. bring next_fs from the right(50%)
                left = (now * 50)+"%";
                //3. increase opacity of next_fs to 1 as it moves in
                opacity = 1 - now;
                current_fs.css({'transform': 'scale('+scale+')'});
                next_fs.css({'left': left, 'opacity': opacity});
            },
            duration: 800,
            complete: function(){
                current_fs.hide();
                animating = false;
            },
            //this comes from the custom easing plugin
            easing: 'easeInOutBack'
        });
    });

    $(".previous").click(function(){
        if(animating) return false;
        animating = true;

        current_fs = $(this).parent();
        previous_fs = $(this).parent().prev();

        //de-activate current step on progressbar
        $("#progressbar li").eq($("fieldset").index(current_fs)).removeClass("active");

        //show the previous fieldset
        previous_fs.show();
        //hide the current fieldset with style
        current_fs.animate({opacity: 0}, {
            step: function(now, mx) {
                //as the opacity of current_fs reduces to 0 - stored in "now"
                //1. scale previous_fs from 80% to 100%
                scale = 0.8 + (1 - now) * 0.2;
                //2. take current_fs to the right(50%) - from 0%
                left = ((1-now) * 50)+"%";
                //3. increase opacity of previous_fs to 1 as it moves in
                opacity = 1 - now;
                current_fs.css({'left': left});
                previous_fs.css({'transform': 'scale('+scale+')', 'opacity': opacity});
            },
            duration: 800,
            complete: function(){
                current_fs.hide();
                animating = false;
            },
            //this comes from the custom easing plugin
            easing: 'easeInOutBack'
        });
    });

    var card = $('.create-specialist-card');
    var errors = card.find('.error');


    $('#specialist_submit').on('click', function(){
        $('#progressbar li').removeClass('invalid').addClass('active');
        $.ajax({
            method: 'POST',
            url: URL,
            data: $('#specialist_form').serializeArray()
        }).done(function (data) {
            if (data.status == 'error') {
                errors.empty();
                for (var i in data.errors) {
                    var errorDiv = card
                        .find('#error_specialist_' + i);
                    errorDiv.html(data.errors[i]);
                    if(i == 'phone'){
                        $('#progressbar li.second-step').removeClass('active').addClass('invalid');
                    }
                    if(i == 'service_id'){
                        $('#progressbar li.first-step').removeClass('active').addClass('invalid');
                    }

                }
            } else {
                window.location.reload()
            }
        });
    });
}

function initLocationAutocomplete() {
    var autocompleteInput = $('#location_autocomplete');
    autocompleteInput.geocomplete({
        details: "#location_details",
        detailsAttribute: "location_attr"
    });
    autocompleteInput.attr('placeholder', '')
}

function addValidationHandlers(){
    $('#specialist_phone').on('keyup', function(){
        $(this).val().length == 13 ?
            $(this).removeClass('invalid').addClass('valid') :
            $(this).removeClass('valid').addClass('invalid')
    });
    $('.materialize-textarea').on('keyup', function(){
        $(this).val().length < 5000 ?
            $(this).removeClass('invalid').addClass('valid') :
            $(this).removeClass('valid').addClass('invalid')
    });
    $('#location_autocomplete').change(function(){
        $(this).addClass('valid');
    });
    $('#specialist_experience').change(function(){
        $(this)
            .closest('.select-wrapper')
            .find('input[type="text"]')
            .addClass('valid');
    });
}

function initServiceSelector(categoryId, apiURL){
    var serviceInput = $('#service_selector');
    var categoryInput = $('#category_selector');
    var selectedServiceIdEl = $('#selected_service_id');

    categoryInput.on('keyup', function(){
        serviceInput.prop('disabled', true);
        categoryInput.addClass('invalid');
        selectedServiceIdEl.val('');
    });
    serviceInput.on('keyup', function(){
        serviceInput.addClass('invalid');
        selectedServiceIdEl.val('');
    });

    initInputAutocomplete(
        serviceInput,
        apiURL,
        {'category': categoryId},
        function (suggestion) {
            $('#selected_service_id')
                .val(suggestion.data);
            serviceInput.addClass('valid').removeClass('invalid');
        });
}
