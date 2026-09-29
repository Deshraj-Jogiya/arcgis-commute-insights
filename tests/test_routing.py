import pytest

from app.routing import RoutingError, drive_route

REDLANDS = (34.0572, -117.1948)  # Esri HQ, same stable address used elsewhere in this repo
CUPERTINO = (37.3318, -122.0296)  # A real, distant California address


def test_real_drive_route_between_two_real_california_addresses():
    result = drive_route(*REDLANDS, *CUPERTINO)

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
    with pytest.raises(RoutingError):
        drive_route(34.0572, -117.1948, 0.0, -160.0)
