from typing import TypeVar

from . import GeoPoint, OverpassResult, haversine


P = TypeVar("P", bound=GeoPoint)


def removeLikelyDuplicates(
    distanceThreshold: int, data: list[P], overpassResult: OverpassResult
) -> list[P]:
    result = []
    for point in data:
        minDistance = distanceThreshold + 1
        for element in overpassResult.allElements():
            minPoint, maxPoint = element.bbox(overpassResult)
            bboxPoints = {
                minPoint,
                maxPoint,
                GeoPoint(minPoint.lat, maxPoint.lon),
                GeoPoint(maxPoint.lat, minPoint.lon),
            }
            for bboxPoint in bboxPoints:
                minDistance = min(minDistance, haversine(point, bboxPoint))
            if minDistance <= distanceThreshold:
                break
        if minDistance > distanceThreshold:
            result.append(point)
    return result
