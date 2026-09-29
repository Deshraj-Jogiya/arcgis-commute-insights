"""Real drive-time/drive-distance routing via the ArcGIS World Route
service (NAServer) -- genuinely different from distance.py's straight-line
haversine estimate: this returns the actual road-network driving distance
and time, plus the route's own real geometry for mapping. Needs a
"Routing" privilege on the ArcGIS API key, separate from Geocoding and
Basemaps (see README's "API key setup" section)."""

import os

import requests

ROUTE_URL = "https://route-api.arcgis.com/arcgis/rest/services/World/Route/NAServer/Route_World/solve"

# The Route service's exact attribute field names have varied across
# ArcGIS API versions/travel modes -- checked defensively against a small
# set of real, documented candidates rather than assumed to be one fixed
# name, so a version difference fails with a clear error instead of a
# silent KeyError.
_MINUTES_FIELD_CANDIDATES = ("Total_TravelTime", "Total_Minutes", "Total_TimeMinutes")
_MILES_FIELD_CANDIDATES = ("Total_Miles", "Total_MilesInDriving")


class RoutingError(Exception):
    pass


def _first_present(attributes: dict, candidates: tuple) -> float:
    for key in candidates:
        if key in attributes:
            return attributes[key]
    raise RoutingError(
        f"None of the expected route attribute fields {candidates} were present "
        f"in the response (got: {sorted(attributes.keys())})"
    )


def drive_route(origin_lat: float, origin_lon: float, dest_lat: float, dest_lon: float, api_key: str | None = None) -> dict:
    """Returns {'drive_minutes', 'drive_miles', 'path'} for the real
    driving route between two points. 'path' is a list of [lat, lon]
    vertices tracing the actual route geometry, suitable for drawing on a
    Leaflet map. Raises RoutingError if no route could be found (e.g. an
    unreachable address, or the API key lacks the Routing privilege)."""
    api_key = api_key or os.environ["ARCGIS_API_KEY"]
    stops = f"{origin_lon},{origin_lat};{dest_lon},{dest_lat}"

    response = requests.get(
        ROUTE_URL,
        params={
            "f": "json",
            "token": api_key,
            "stops": stops,
            "returnRoutes": "true",
            "returnDirections": "false",
        },
        timeout=15,
    )
    response.raise_for_status()
    data = response.json()

    if "error" in data:
        raise RoutingError(data["error"].get("message", "Unknown ArcGIS routing error"))

    features = data.get("routes", {}).get("features", [])
    if not features:
        raise RoutingError("No drivable route found between the given points")

    route = features[0]
    attrs = route["attributes"]
    vertices = route["geometry"]["paths"][0]

    return {
        "drive_minutes": round(_first_present(attrs, _MINUTES_FIELD_CANDIDATES), 1),
        "drive_miles": round(_first_present(attrs, _MILES_FIELD_CANDIDATES), 2),
        "path": [[lat, lon] for lon, lat in vertices],
    }
