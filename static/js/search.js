function initSearchPage(currentServiceId, specialistsCount, currentPage){
    specialistCardHandler();
    paginationHandler(currentServiceId, specialistsCount, currentPage)
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

function paginationHandler(currentServiceId, specialistsCount, currentPage) {
    var pagesCount = parseInt(specialistsCount / 12);
    if (specialistsCount - pagesCount * 12 != 0) {
        pagesCount = pagesCount + 1
    }

    var pagination = $('.page-numbers');

    _.forEach(_.range(1, pagesCount + 1), function (pageNum) {
        pagination.append(
            '<li class="waves-effect page-number">' +
            '<a href="/service/' + currentServiceId + '?page='
            + pageNum + '" id="' + pageNum + '">' + pageNum + '</a>' +
            '</li>')
    });

    var pageNumberEl = $('.page-number');

    //if (currentPage > 9){
    if (currentPage > 5){
        pageNumberEl.slice(1, currentPage - 5).hide();
    }
    if (currentPage < pagesCount - 5) {
        pageNumberEl.slice(currentPage + 4, pagesCount - 1).hide();
    }
    //pageNumberEl.slice(currentPage - 6, currentPage + 5).show();
    //}

    var nextEl = $('#next_page');
    var previousEl = $('#previous_page');
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