import pytest

from app.distance import haversine_miles


def test_zero_distance_for_the_same_point():
    assert haversine_miles(34.0572, -117.1948, 34.0572, -117.1948) == pytest.approx(0.0, abs=1e-6)


def test_known_real_distance_los_angeles_to_new_york():
    # Real, well-known great-circle distance LAX <-> JFK is ~2,475 miles.
    lax = (33.9416, -118.4085)
    jfk = (40.6413, -73.7781)
    distance = haversine_miles(*lax, *jfk)
    assert distance == pytest.approx(2475, rel=0.02)
