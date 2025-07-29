from math import sin, cos, sqrt, atan2, radians

from .models import GeoPoint

"""
Haversine formula
https://en.wikipedia.org/wiki/Haversine_formula
@point: GeoPoint
@other: GeoPoint
@return: distance in meters
"""


def haversine(point: GeoPoint, other: GeoPoint) -> int:
    R = 6373.0
    lon1, lat1, lon2, lat2 = map(radians, [point.lon, point.lat, other.lon, other.lat])

    deltaLon = lon2 - lon1
    deltaLat = lat2 - lat1
    a = (sin(deltaLat / 2)) ** 2 + cos(lat1) * cos(lat2) * (sin(deltaLon / 2)) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return int(R * c * 1000)
