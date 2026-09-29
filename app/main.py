"""CLI: geocode a home address and a list of company addresses via the
real ArcGIS World Geocoding Service, rank companies by real drive time
(falling back to straight-line great-circle distance when no route can be
found), show real basemap layer/feature data for the home area, and write
a real interactive map (Leaflet, with the actual routed geometry where
available) to disk.

Usage:
    python -m app.main "home address" "company 1" "company 2" ...
"""

import sys

from .distance import haversine_miles
from .geocoding import GeocodingError, geocode_address
from .map_export import write_map_html
from .routing import RoutingError, drive_route
from .tiles import basemap_layers_near

DEFAULT_MAP_PATH = "commute_map.html"


def analyze(home_address: str, company_addresses: list[str]) -> dict:
    home = geocode_address(home_address)

    companies = []
    for addr in company_addresses:
        try:
            company = geocode_address(addr)
        except GeocodingError:
            continue

        company["distance_miles"] = round(
            haversine_miles(home["lat"], home["lon"], company["lat"], company["lon"]), 2
        )

        # Real drive-time routing, with a graceful fallback: an
        # unreachable address, a rate limit, or a key that hasn't been
        # granted the Routing privilege yet should degrade to the
        # straight-line estimate rather than fail the whole analysis.
        try:
            route = drive_route(home["lat"], home["lon"], company["lat"], company["lon"])
            company["drive_minutes"] = route["drive_minutes"]
            company["drive_miles"] = route["drive_miles"]
            company["path"] = route["path"]
        except RoutingError:
            company["drive_minutes"] = None
            company["drive_miles"] = None
            company["path"] = None

        companies.append(company)

    companies.sort(key=lambda c: c["drive_minutes"] if c["drive_minutes"] is not None else c["distance_miles"])

    basemap_layers = basemap_layers_near(home["lat"], home["lon"])

    return {"home": home, "companies": companies, "basemap_layers_near_home": basemap_layers}


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python -m app.main <home address> <company address> [more addresses...]")
        sys.exit(1)

    home_address, *company_addresses = sys.argv[1:]
    result = analyze(home_address, company_addresses)

    print(f"Home: {result['home']['address']} ({result['home']['lat']:.5f}, {result['home']['lon']:.5f})")
    print("\nCompanies by drive time (falls back to straight-line distance if no route found):")
    for c in result["companies"]:
        if c["drive_minutes"] is not None:
            print(f"  {c['drive_minutes']:>6.1f} min ({c['drive_miles']:.2f} mi by road)  -  {c['address']}")
        else:
            print(f"  {c['distance_miles']:>7.2f} mi straight-line (no route found)  -  {c['address']}")

    print("\nReal basemap layers near home (from a live vector tile):")
    for layer, count in sorted(result["basemap_layers_near_home"].items()):
        print(f"  {layer}: {count} feature(s)")

    write_map_html(DEFAULT_MAP_PATH, result["home"], result["companies"])
    print(f"\nWrote a real interactive map to {DEFAULT_MAP_PATH}")


if __name__ == "__main__":
    main()
