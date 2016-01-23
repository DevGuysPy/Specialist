function searchAutocomplete(apiURL){
    $('#main_search').autocomplete({
        serviceUrl: apiURL,
        onSelect: function (suggestion) {
            window.location = '/service/' + suggestion.data;
        }
    })
}
