"""Real geocoding via the ArcGIS World Geocoding Service -- turns a
free-text address into real coordinates. Requires a real ArcGIS API
key with the Geocoding privilege (developers.arcgis.com)."""

import os

import requests

GEOCODE_URL = "https://geocode-api.arcgis.com/arcgis/rest/services/World/GeocodeServer/findAddressCandidates"


class GeocodingError(Exception):
    pass


def geocode_address(address: str, api_key: str | None = None) -> dict:
    """Returns {'address', 'lat', 'lon', 'score'} for the best match, or
    raises GeocodingError if nothing was found."""
    api_key = api_key or os.environ["ARCGIS_API_KEY"]

    response = requests.get(
        GEOCODE_URL,
        params={"SingleLine": address, "f": "json", "token": api_key, "maxLocations": 1},
        timeout=10,
    )
    response.raise_for_status()
    data = response.json()

    candidates = data.get("candidates", [])
    if not candidates:
        raise GeocodingError(f"No geocoding match found for {address!r}")

    best = candidates[0]
    return {
        "address": best["address"],
        "lat": best["location"]["y"],
        "lon": best["location"]["x"],
        "score": best["score"],
    }
