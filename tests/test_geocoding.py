import pytest

from app.geocoding import GeocodingError, geocode_address


def test_geocodes_a_real_well_known_address():
    # 380 New York St, Redlands, CA is Esri's real corporate HQ -- a
    # stable, well-known address good for a real integration test.
    result = geocode_address("380 New York St, Redlands, CA")

    assert result["score"] >= 90
    assert result["lat"] == pytest.approx(34.0572, abs=0.01)
    assert result["lon"] == pytest.approx(-117.1948, abs=0.01)


def test_raises_a_real_error_for_nonsense_input():
    with pytest.raises(GeocodingError):
        geocode_address("zzzzznonexistentplacezzzzz1234567890")
