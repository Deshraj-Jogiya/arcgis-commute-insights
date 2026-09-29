import json

from app.map_export import build_map_html


def test_builds_html_embedding_the_real_home_and_company_data():
    home = {"address": "380 New York St, Redlands, CA", "lat": 34.0572, "lon": -117.1948}
    companies = [
        {
            "address": "1 Infinite Loop, Cupertino, CA",
            "lat": 37.3318,
            "lon": -122.0296,
            "distance_miles": 380.5,
            "drive_minutes": 340.2,
            "drive_miles": 390.1,
            "path": [[34.0572, -117.1948], [37.3318, -122.0296]],
        },
    ]

    html = build_map_html(home, companies)

    assert "leaflet" in html.lower()
    assert "1 Infinite Loop" in html
    assert json.dumps(home) in html


def test_handles_a_company_with_no_route_found_without_crashing():
    home = {"address": "Home", "lat": 1.0, "lon": 2.0}
    companies = [
        {
            "address": "Nowhere",
            "lat": 3.0,
            "lon": 4.0,
            "distance_miles": 100.0,
            "drive_minutes": None,
            "drive_miles": None,
            "path": None,
        }
    ]

    html = build_map_html(home, companies)

    assert "Nowhere" in html
    assert "null" in html  # drive_minutes serialized as JSON null, not a crash
