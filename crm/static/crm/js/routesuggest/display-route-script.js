function initMap() {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 34.710734511056266, lng: 137.85243458835393 },
    });

    directionsRenderer.setMap(map);

    displayRoute(
        route_suggest_list,
        directionsService,
        directionsRenderer,
    );
}

/**
 * @param route_suggest_list
 * @param service directionsService
 * @param display directionsRenderer
 * @see https://developers.google.com/maps/documentation/javascript/reference/directions?hl=ja#DirectionsRequest
 */
function displayRoute(route_suggest_list, service, display) {
    if (route_suggest_list.length < 2) {
        alert("少なくとも 2 つの場所を指定してください");
        return;
    }
    if (route_suggest_list.length > 8) {
        alert("場所が多すぎます。許可される最大場所数は 8 です");
        return;
    }

    service
        .route({
            origin: route_suggest_list.shift(),
            destination: route_suggest_list.pop(),
            waypoints: route_suggest_list.map(location => ({ location })),
            travelMode: google.maps.TravelMode.DRIVING,
            avoidTolls: true,  // 有料道路を除外
            optimizeWaypoints: true  // 地点最適化
        })
        .then((result) => {
            display.setDirections(result);
        })
        .catch((e) => {
            alert("Could not display directions due to: " + e);
        });
}
window.initMap = initMap;
