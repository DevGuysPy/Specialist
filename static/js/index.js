function searchAutocomplete(apiURL){
    $('.search-input').autocomplete({
        serviceUrl: apiURL,
        onSelect: function (suggestion) {
            window.location = '/service/' + suggestion.data;
        }
    })
}
