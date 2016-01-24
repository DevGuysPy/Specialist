function initSearchPage(){
    specialistCardHandler()
}

function specialistCardHandler(){
    var cards = $('.specialist-card');
    cards.find('img, .card-title').on('click', function(){
        window.location = '/account/' + $(this)
                .closest('.specialist-card')
                .find('input[class="specialist-id"]')
                .val()
    });


    function limitText(el){
        var text = el.text();
        el.text(text.substr(0, 150));
        el.append(' <a class="show-description">Show more</a>' +
        '<span class="hidden-text" style="display: none;">' + text.substr(150 , text.length) + '</span>');
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