from starsep_utils import removeLikelyDuplicates, GeoPoint
from .overpass_test import expectedOverpassResult


def test_removeLikelyDuplicates():
    assert removeLikelyDuplicates(100, [], expectedOverpassResult) == []

    points = [
        GeoPoint(lat=52.01, lon=21.01),
        GeoPoint(lat=52.05, lon=21.01),
        GeoPoint(lat=52.02, lon=21.01005),
        GeoPoint(lat=52.02, lon=21.02),
        GeoPoint(lat=52.03, lon=21.011),
        GeoPoint(lat=52.03, lon=21.012),
    ]
    assert removeLikelyDuplicates(100, points, expectedOverpassResult) == [
        points[1],
        points[3],
        points[5],
    ]
