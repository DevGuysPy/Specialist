$( document ).ready(function() {
    var cards = $('.collection-item');
    cards.each(function () {
        function limitText(el) {
            var text = el.text();
            el.text(text.substr(0, 40));
            el.append('<span class="for-hiding">... </span>' + '<a class="show-description">more</a>' +
                '<span class="hidden-text" style="display: none;">' + text.substr(40, text.length) + '</span>');
        }

        var textEl = $(this)
            .find('.description')
            .find('.description-text');
        textEl.text().length >= 40 ?
            limitText(textEl) : null
    });
    $('.show-description').on('click', function (e) {
        $(this).hide();
        $(this).parent().find('.hidden-text').show();
        $('.for-hiding').hide();
    });
});