function initMap() {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 34.710734511056266, lng: 137.85243458835393 },
    });

    directionsRenderer.setMap(map);

    displayRoute(
        coords_list,
        directionsService,
        directionsRenderer,
    );
}

/**
 * @param coords_list
 * @param service directionsService
 * @param display directionsRenderer
 * @see https://developers.google.com/maps/documentation/javascript/reference/directions?hl=ja#DirectionsRequest
 */
function displayRoute(coords_list, service, display) {
    service
        .route({
            origin: coords_list.shift(),
            destination: coords_list.pop(),
            waypoints: coords_list.map(location => ({ location })),
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
