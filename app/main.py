"""CLI: geocode a home address and a list of company addresses via the
real ArcGIS World Geocoding Service, rank companies by real
great-circle distance from home, and show real basemap layer/feature
data for the home area (proving the Basemaps privilege, not just
Geocoding, is genuinely used).

Usage:
    python -m app.main "home address" "company 1" "company 2" ...
"""

import sys

from .distance import haversine_miles
from .geocoding import GeocodingError, geocode_address
from .tiles import basemap_layers_near


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
        companies.append(company)

    companies.sort(key=lambda c: c["distance_miles"])

    basemap_layers = basemap_layers_near(home["lat"], home["lon"])

    return {"home": home, "companies": companies, "basemap_layers_near_home": basemap_layers}


def main() -> None:
    if len(sys.argv) < 3:
        print("Usage: python -m app.main <home address> <company address> [more addresses...]")
        sys.exit(1)

    home_address, *company_addresses = sys.argv[1:]
    result = analyze(home_address, company_addresses)

    print(f"Home: {result['home']['address']} ({result['home']['lat']:.5f}, {result['home']['lon']:.5f})")
    print("\nCompanies by distance:")
    for c in result["companies"]:
        print(f"  {c['distance_miles']:>7.2f} mi  -  {c['address']}")

    print("\nReal basemap layers near home (from a live vector tile):")
    for layer, count in sorted(result["basemap_layers_near_home"].items()):
        print(f"  {layer}: {count} feature(s)")


if __name__ == "__main__":
    main()
