"""Builds a real, self-contained interactive map (Leaflet.js via CDN, no
build step) from the real geocoded home/company coordinates and, where a
drive route was found, the route's own real geometry -- so the tool
produces something to actually look at, not just console text."""

import json

_HTML_TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>Commute Map</title>
  <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css">
  <style>
    body {{ margin: 0; font-family: -apple-system, "Segoe UI", sans-serif; }}
    #map {{ height: 100vh; width: 100%; }}
    .legend {{ position: absolute; top: 10px; right: 10px; z-index: 1000; background: #fff;
               padding: 0.75rem 1rem; border-radius: 8px; box-shadow: 0 1px 4px rgba(0,0,0,0.3); }}
  </style>
</head>
<body>
  <div id="map"></div>
  <div class="legend">
    <strong>Commute Map</strong>
    <div id="summary"></div>
  </div>
  <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
  <script>
    const homeMarker = {home_json};
    const companies = {companies_json};

    const map = L.map('map').setView([homeMarker.lat, homeMarker.lon], 11);
    L.tileLayer('https://{{s}}.tile.openstreetmap.org/{{z}}/{{x}}/{{y}}.png', {{
      attribution: '&copy; OpenStreetMap contributors'
    }}).addTo(map);

    L.marker([homeMarker.lat, homeMarker.lon]).addTo(map)
      .bindPopup('<strong>Home</strong><br>' + homeMarker.address);

    const bounds = [[homeMarker.lat, homeMarker.lon]];
    let routedCount = 0;

    companies.forEach((c) => {{
      L.marker([c.lat, c.lon]).addTo(map)
        .bindPopup(
          '<strong>' + c.address + '</strong><br>' +
          (c.drive_minutes != null
            ? c.drive_minutes + ' min drive (' + c.drive_miles + ' mi by road)'
            : c.distance_miles + ' mi straight-line (no route found)')
        );
      bounds.push([c.lat, c.lon]);

      if (c.path && c.path.length > 1) {{
        L.polyline(c.path, {{ color: '#2f6f4f', weight: 3, opacity: 0.8 }}).addTo(map);
        routedCount++;
      }}
    }});

    map.fitBounds(bounds, {{ padding: [40, 40] }});

    document.getElementById('summary').textContent =
      companies.length + ' compan' + (companies.length === 1 ? 'y' : 'ies') +
      ', ' + routedCount + ' with a real driving route';
  </script>
</body>
</html>
"""


def build_map_html(home: dict, companies: list[dict]) -> str:
    """home: {'address', 'lat', 'lon'}. companies: list of dicts each with
    at least 'address', 'lat', 'lon', 'distance_miles', and optionally
    'drive_minutes'/'drive_miles'/'path' when a real route was found."""
    return _HTML_TEMPLATE.format(
        home_json=json.dumps(home),
        companies_json=json.dumps(companies),
    )


def write_map_html(path: str, home: dict, companies: list[dict]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(build_map_html(home, companies))
