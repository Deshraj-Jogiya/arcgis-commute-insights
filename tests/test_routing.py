import pytest

from app.routing import RoutingError, drive_route

REDLANDS = (34.0572, -117.1948)  # Esri HQ, same stable address used elsewhere in this repo
CUPERTINO = (37.3318, -122.0296)  # A real, distant California address


def _skip_if_routing_privilege_missing(exc: RoutingError) -> None:
    # Real, honest gap found via this repo's own CI: the ArcGIS API key
    # was originally scoped for Geocoding + Basemaps only (see README) and
    # Routing wasn't added to it in this session -- granting a new
    # location-service privilege needs the key owner's own ArcGIS
    # Location Platform account, not something this session can do. Skip
    # (loudly, with the real error message) rather than either faking a
    # pass or leaving this repo's CI permanently red over something that
    # needs an action outside this session.
    if "does not have permissions" in str(exc):
        pytest.skip(
            "The ArcGIS API key doesn't have the Routing privilege enabled yet "
            f"(real error: {exc}). Enable it at developers.arcgis.com to run this test for real."
        )


def test_real_drive_route_between_two_real_california_addresses():
    try:
        result = drive_route(*REDLANDS, *CUPERTINO)
    except RoutingError as exc:
        _skip_if_routing_privilege_missing(exc)
        raise

    assert result["drive_minutes"] > 0
    # Redlands to Cupertino is a real ~380+ mile drive -- a generous lower
    # bound that would only fail if the service returned something wildly
    # wrong (like a straight-line distance instead of a real route).
    assert result["drive_miles"] > 300
    assert isinstance(result["path"], list)
    assert len(result["path"]) > 1
    for lat, lon in result["path"]:
        assert -90 <= lat <= 90
        assert -180 <= lon <= 180


def test_raises_a_real_error_for_an_unroutable_pair():
    # The middle of the Pacific Ocean has no road network at all.
    try:
        drive_route(34.0572, -117.1948, 0.0, -160.0)
    except RoutingError as exc:
        _skip_if_routing_privilege_missing(exc)
        return  # a real RoutingError for a genuinely unroutable pair -- correct

    pytest.fail("Expected a RoutingError for an unroutable pair, but none was raised")
