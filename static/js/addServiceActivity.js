function substringMatcher(strs) {
  return function findMatches(q, cb) {
    var matches, substringRegex;

    // an array that will be populated with substring matches
    matches = [];

    // regex used to determine if a string contains the substring `q`
    substrRegex = new RegExp(q, 'i');

    // iterate through the pool of strings and for any string that
    // contains the substring `q`, add it to the `matches` array
    $.each(strs, function(i, str) {
      if (substrRegex.test(str)) {
        matches.push(str);
      }
    });

    cb(matches);
  };
}

function initServiceActivity(specialists, customers, services){
    addTypeahead('specialist', specialists);
    addTypeahead('customer', customers);
    addTypeahead('service', services)
}

function addTypeahead(item, data) {
    var typeaheadEl = $('#' + item + '.typeahead');
    var choices = [];
    _.each(data, function(item){
        choices.push(item['name'])
    });
    typeaheadEl.typeahead({
            hint: true,
            highlight: true,
            minLength: 1
        },
        {
            name: item,
            source: substringMatcher(choices)
        });
    typeaheadEl.on('typeahead:select', function(){
        $('input[id="' + item + '_id"]').val(
            parseInt(data[_.findIndex(data, {'name': $(this).val()})]['id']));
    })
}