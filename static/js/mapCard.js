function initCardMap(userLatitude, userLongitude, location){
    // Google Maps
    $('#map-canvas').addClass('loading');
    var latlng = new google.maps.LatLng(userLatitude, userLongitude); // Set your Lat. Log. New York
    var settings = {
        zoom: 10,
        center: latlng,
        mapTypeId: google.maps.MapTypeId.ROADMAP,
        mapTypeControl: false,
        scrollwheel: false,
        draggable: true,
        styles: [{"featureType":"landscape.natural","elementType":"geometry.fill","stylers":[{"visibility":"on"},
            {"color":"#e0efef"}]},{"featureType":"poi","elementType":"geometry.fill","stylers":[{"visibility":"on"},
            {"hue":"#1900ff"},{"color":"#c0e8e8"}]},{"featureType":"road","elementType":"geometry",
            "stylers":[{"lightness":100},{"visibility":"simplified"}]},{"featureType":"road","elementType":"labels"
            ,"stylers":[{"visibility":"off"}]},{"featureType":"transit.line","elementType":"geometry",
            "stylers":[{"visibility":"on"},{"lightness":700}]},{"featureType":"water","elementType":"all",
            "stylers":[{"color":"#7dcdcd"}]}],
        mapTypeControlOptions: {style: google.maps.MapTypeControlStyle.DROPDOWN_MENU},
        navigationControl: false,
        navigationControlOptions: {style: google.maps.NavigationControlStyle.SMALL},
    };
    var map = new google.maps.Map(document.getElementById("map-canvas"), settings);

    google.maps.event.addDomListener(window, "resize", function() {
        var center = map.getCenter();
        google.maps.event.trigger(map, "resize");
        map.setCenter(center);
        $('#map-canvas').removeClass('loading');
    });

    var contentString =
        '<div id="info-window">'+
        '<p>' + location +'</p>'+
        '</div>';
    var infowindow = new google.maps.InfoWindow({
        content: contentString
    });

    var companyImage = new google.maps.MarkerImage('https://goo.gl/uY6Q0I',
        new google.maps.Size(36,62),// Width and height of the marker
        new google.maps.Point(0,0),
        new google.maps.Point(18,52)// Position of the marker
    );

    var companyPos = new google.maps.LatLng(userLatitude, userLongitude);

    var companyMarker = new google.maps.Marker({
        position: companyPos,
        map: map,
        icon: companyImage,
        title:"Shapeshift Interactive",
        zIndex: 3});

    google.maps.event.addListener(companyMarker, 'click', function() {
        infowindow.open(map,companyMarker);
        pageView('/#address');
    });
};