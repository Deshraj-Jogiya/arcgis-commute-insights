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
  needed for this part -- used as the ranking metric when a real drive route
  couldn't be found (see below).
- **Drive-time routing**: `app/routing.py` calls the live ArcGIS World Route
  service (`NAServer/Route_World/solve`) for a real road-network driving time
  and distance between home and each company, plus the route's own real
  geometry. Companies are ranked by real drive time when a route is found,
  falling back to straight-line distance otherwise (an unreachable address, a
  transient error, or an API key without the Routing privilege yet -- see "API
  key setup" below).
- **Interactive map**: `app/map_export.py` writes a real, self-contained
  `commute_map.html` (Leaflet.js via CDN, OpenStreetMap tiles, no build step)
  plotting the real geocoded home/company markers and, where routing
  succeeded, the actual routed polyline -- not just console text.

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

Every ArcGIS-hitting test (geocoding, tile fetch + decode, drive-time routing) is a
real, live call -- no mocks. One test locks in a hand-verified tile coordinate
(`latlon_to_tile` for Esri's real HQ address, checked against the actual
slippy-map grid before being hardcoded as the expected value), another asserts on
real observed basemap layer names (`Road`, `Land`) rather than invented ones, and
the routing tests check real, sane bounds on a genuine ~380-mile CA drive rather
than an exact value that could drift with real-world road changes. The map-export
tests are plain unit tests (no network) since they only format already-fetched
data into HTML.

## API key setup

Needs an [ArcGIS Location Platform](https://developers.arcgis.com) API key
(free tier) with the **Geocoding**, **Basemaps**, and **Routing** location-service
privileges enabled, scoped as a "Public application" credential with no item
access (the least-privilege option for this kind of scripted use). Routing was
added after Geocoding/Basemaps were first set up -- if the key predates this
and hasn't had Routing enabled yet, `drive_route` calls will fail and the
tool falls back to straight-line distance automatically (a real, visible
`RoutingError`, not a silent wrong number); enable it on the key's page at
developers.arcgis.com to get real drive-time ranking.
