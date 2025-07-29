import pytest

from starsep_utils import GeoPoint, haversine


def test_haversine():
    testCases = [
        (
            GeoPoint(lat=52.263298, lon=21.046161),
            GeoPoint(lat=52.2602571, lon=21.0468360),
            341,
            0,
        ),
        (
            GeoPoint(lat=52.263298, lon=21.046161),
            GeoPoint(lat=52.263298, lon=21.046161),
            0,
            0,
        ),
        (
            GeoPoint(lat=52.2157063, lon=20.9602140),
            GeoPoint(lat=52.205017, lon=21.168801),
            14307,
            0.01,
        ),
    ]
    for pointA, pointB, expected, rel in testCases:
        assert haversine(pointA, pointB) == pytest.approx(expected, rel)
