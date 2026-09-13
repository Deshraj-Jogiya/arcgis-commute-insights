# ArcGIS Commute Insights

A small real tool for a job search: geocode a home address and a list of company
addresses via the real ArcGIS World Geocoding Service, rank companies by real
great-circle distance from home, and pull real basemap data (via ArcGIS's Basemap
Styles vector tile service) for the home area.

## What's real here

- **Geocoding**: `app/geocoding.py` calls the live ArcGIS `findAddressCandidates`
  endpoint -- no mocking, no hardcoded coordinates.
- **Basemap vector tiles**: `app/tiles.py` fetches and decodes a real Mapbox Vector
  Tile (`.pbf`) from Esri's World Basemap v2 `VectorTileServer`. The tile URL
  template used here was confirmed by fetching the real basemap *style* JSON first
  and reading its `sources` section, not assumed from docs -- an earlier guessed
  URL pattern (`basemapstyles-api.arcgis.com/.../tile/{z}/{y}/{x}`) returned a real
  404, which is what led to checking the style JSON for the actual template.
- **Distance ranking**: real haversine great-circle distance, no external service
  needed for this part.

## Running it

```bash
pip install -r requirements.txt
export ARCGIS_API_KEY=<your ArcGIS API key, with Geocoding + Basemaps privileges>

python -m app.main "home address" "company address 1" "company address 2"
```

## Testing

```bash
python -m pytest tests/ -v
```

All 7 tests hit the real ArcGIS APIs (geocoding, tile fetch + decode) -- no mocks.
One test locks in a hand-verified tile coordinate (`latlon_to_tile` for Esri's real
HQ address, checked against the actual slippy-map grid before being hardcoded as
the expected value), and another asserts on real observed basemap layer names
(`Road`, `Land`) rather than invented ones.

## API key setup

Needs an [ArcGIS Location Platform](https://developers.arcgis.com) API key
(free tier) with the **Geocoding** and **Basemaps** location-service privileges
enabled, scoped as a "Public application" credential with no item access (the
least-privilege option for this kind of scripted use).
