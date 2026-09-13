"""Real basemap vector-tile access via Esri's World Basemap v2
VectorTileServer -- fetches and decodes the actual Mapbox Vector Tile
(MVT/.pbf) protobuf covering a given coordinate, using the real
ArcGIS API key's Basemaps privilege. The tile URL template here (and
the fact that this basemap serves genuine vector tiles, not
pre-rendered raster images) was confirmed by fetching the real style
JSON from the Basemap Styles service and reading its `sources`
section -- not assumed from documentation."""

import math
import os

import requests
from mapbox_vector_tile import decode as decode_mvt

TILE_URL_TEMPLATE = (
    "https://basemaps-api.arcgis.com/arcgis/rest/services/"
    "World_Basemap_v2/VectorTileServer/tile/{z}/{y}/{x}.pbf"
)


def latlon_to_tile(lat: float, lon: float, zoom: int) -> tuple[int, int]:
    """Standard slippy-map tile math (Web Mercator)."""
    lat_rad = math.radians(lat)
    n = 2**zoom
    xtile = int((lon + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + 1 / math.cos(lat_rad)) / math.pi) / 2.0 * n)
    return xtile, ytile


def fetch_vector_tile(z: int, x: int, y: int, api_key: str | None = None) -> bytes:
    api_key = api_key or os.environ["ARCGIS_API_KEY"]
    url = TILE_URL_TEMPLATE.format(z=z, y=y, x=x)

    response = requests.get(url, params={"token": api_key}, timeout=10)
    response.raise_for_status()
    return response.content


def decode_tile_layers(tile_bytes: bytes) -> dict[str, int]:
    """Decodes the real MVT protobuf and returns {layer_name: feature_count}."""
    decoded = decode_mvt(tile_bytes)
    return {layer_name: len(layer["features"]) for layer_name, layer in decoded.items()}


def basemap_layers_near(lat: float, lon: float, zoom: int = 12, api_key: str | None = None) -> dict[str, int]:
    """Convenience wrapper: real coordinate in, real decoded layer/feature
    counts for the basemap tile covering it, out."""
    x, y = latlon_to_tile(lat, lon, zoom)
    tile_bytes = fetch_vector_tile(zoom, x, y, api_key=api_key)
    return decode_tile_layers(tile_bytes)
