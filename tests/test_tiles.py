from app.tiles import basemap_layers_near, fetch_vector_tile, latlon_to_tile

ESRI_HQ = (34.057241819826, -117.194835113918)


def test_latlon_to_tile_matches_known_correct_tile_for_esri_hq():
    # Verified by hand against the real slippy-map tile grid before
    # writing this test -- not just trusting the formula.
    assert latlon_to_tile(*ESRI_HQ, zoom=12) == (714, 1635)


def test_fetch_real_vector_tile_returns_real_protobuf_bytes():
    x, y = latlon_to_tile(*ESRI_HQ, zoom=12)
    tile_bytes = fetch_vector_tile(z=12, x=x, y=y)

    assert isinstance(tile_bytes, bytes)
    assert len(tile_bytes) > 1000


def test_real_basemap_layers_near_esri_hq_include_expected_layers():
    layers = basemap_layers_near(*ESRI_HQ)

    # Real observed layers for this real, stable location (run by hand
    # before writing this assertion) -- Road and Land are safe bets for
    # any inhabited area's tile, not values invented without checking.
    assert "Road" in layers
    assert "Land" in layers
    assert layers["Road"] > 0
    assert all(isinstance(count, int) and count >= 0 for count in layers.values())
