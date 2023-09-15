function initMap() {
    const directionsService = new google.maps.DirectionsService();
    const directionsRenderer = new google.maps.DirectionsRenderer();
    const map = new google.maps.Map(document.getElementById("map"), {
        zoom: 7,
        center: { lat: 34.710734511056266, lng: 137.85243458835393 },
    });

    directionsRenderer.setMap(map);

    displayRoute(
        "磐田駅",  // TODO: 出発地
        "浜松駅",  // TODO: 到着地
        directionsService,
        directionsRenderer,
    );
}

/**
 * @param origin 出発地
 * @param destination 到着地
 * @param service directionsService
 * @param display directionsRenderer
 * @see https://developers.google.com/maps/documentation/javascript/reference/directions?hl=ja#DirectionsRequest
 */
function displayRoute(origin, destination, service, display) {
    service
        .route({
            origin: origin,
            destination: destination,
            waypoints: [
                { location: "浜松鑑定団" },  // TODO: 経由地1
                { location: "磐田市香りの博物館" },  //TODO: 経由地2
            ],
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
