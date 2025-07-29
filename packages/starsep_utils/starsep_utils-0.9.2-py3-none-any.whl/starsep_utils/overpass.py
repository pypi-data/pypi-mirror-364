import abc
import json
import logging
from dataclasses import dataclass

from httpx import AsyncClient

from . import GeoPoint
from .logDuration import logDuration


DEFAULT_OVERPASS_URL = "https://overpass-api.de/api/interpreter"
client = AsyncClient(timeout=None)


class KeyDict(dict):
    def __hash__(self):
        return hash(frozenset(self.items()))


Bbox = tuple[GeoPoint, GeoPoint]


@dataclass(frozen=True)
class Element(abc.ABC):
    id: int
    type: str
    tags: KeyDict

    @property
    def url(self):
        return f"https://osm.org/{self.type}/{self.id}"

    @abc.abstractmethod
    def center(self, overpassResult: "OverpassResult") -> GeoPoint:
        raise NotImplementedError

    @abc.abstractmethod
    def bbox(self, overpassResult: "OverpassResult") -> Bbox:
        raise NotImplementedError


@dataclass(frozen=True)
class Node(Element, GeoPoint):
    def bbox(self, overpassResult: "OverpassResult") -> Bbox:
        return GeoPoint(lat=self.lat, lon=self.lon), GeoPoint(
            lat=self.lat, lon=self.lon
        )

    def center(self, overpassResult: "OverpassResult") -> GeoPoint:
        return GeoPoint(lat=self.lat, lon=self.lon)


@dataclass(frozen=True)
class Way(Element):
    nodes: list[int]

    def center(self, overpassResult: "OverpassResult") -> GeoPoint:
        centers = [
            overpassResult.nodes[nodeId].center(overpassResult) for nodeId in self.nodes
        ]
        lat = sum(center.lat for center in centers) / len(centers)
        lon = sum(center.lon for center in centers) / len(centers)
        return GeoPoint(lat=lat, lon=lon)

    def bbox(self, overpassResult: "OverpassResult") -> Bbox:
        minLat, minLon, maxLat, maxLon = (
            float("inf"),
            float("inf"),
            float("-inf"),
            float("-inf"),
        )
        for nodeId in self.nodes:
            node = overpassResult.nodes[nodeId]
            minLat = min(minLat, node.lat)
            minLon = min(minLon, node.lon)
            maxLat = max(maxLat, node.lat)
            maxLon = max(maxLon, node.lon)
        return GeoPoint(lat=minLat, lon=minLon), GeoPoint(lat=maxLat, lon=maxLon)


@dataclass(frozen=True)
class RelationMember:
    type: str
    id: int
    role: str


@dataclass(frozen=True)
class Relation(Element):
    members: list[RelationMember]

    def center(self, overpassResult: "OverpassResult") -> GeoPoint:
        raise NotImplementedError

    def bbox(self, overpassResult: "OverpassResult") -> Bbox:
        minLat, minLon, maxLat, maxLon = (
            float("inf"),
            float("inf"),
            float("-inf"),
            float("-inf"),
        )
        for member in self.members:
            element = overpassResult.resolve(member)
            bbox = element.bbox(overpassResult)
            minLat = min(minLat, bbox[0].lat)
            minLon = min(minLon, bbox[0].lon)
            maxLat = max(maxLat, bbox[1].lat)
            maxLon = max(maxLon, bbox[1].lon)
        return GeoPoint(lat=minLat, lon=minLon), GeoPoint(lat=maxLat, lon=maxLon)


@dataclass(frozen=True)
class OverpassResult:
    nodes: dict[int, Node]
    ways: dict[int, Way]
    relations: dict[int, Relation]

    def resolve(self, member: RelationMember) -> Element:
        if member.type == "node":
            return self.nodes[member.id]
        if member.type == "way":
            return self.ways[member.id]
        if member.type == "relation":
            return self.relations[member.id]
        raise ValueError(member.type)

    def allElements(self) -> list[Element]:
        return (
            list(self.nodes.values())
            + list(self.ways.values())
            + list(self.relations.values())
        )


async def _getOverpassHttpx(query: str, overpassUrl: str):
    with logDuration("Downloading data from Overpass"):
        jsonQuery = f"[out:json][timeout:250];\n{query}"
        response = await client.post(overpassUrl, data=dict(data=jsonQuery))
        response.raise_for_status()
    with logDuration("Parsing Overpass JSON"):
        return json.loads(response.text)["elements"]


@logDuration
def _parseOverpassData(parsedElements: list[dict]) -> OverpassResult:
    nodes, ways, relations = dict(), dict(), dict()
    for element in parsedElements:
        if element["type"] == "node":
            nodes[element["id"]] = Node(
                id=element["id"],
                type=element["type"],
                lat=element["lat"],
                lon=element["lon"],
                tags=KeyDict(element.get("tags", dict())),
            )
        if element["type"] == "way":
            ways[element["id"]] = Way(
                id=element["id"],
                type=element["type"],
                nodes=element["nodes"],
                tags=KeyDict(element.get("tags", dict())),
            )
        if element["type"] == "relation":
            members = [
                RelationMember(
                    type=member["type"], id=member["ref"], role=member["role"]
                )
                for member in element["members"]
            ]
            relations[element["id"]] = Relation(
                id=element["id"],
                type=element["type"],
                members=members,
                tags=KeyDict(element.get("tags", dict())),
            )
    return OverpassResult(nodes=nodes, ways=ways, relations=relations)


async def downloadOverpassData(
    query: str, overpassUrl: str = DEFAULT_OVERPASS_URL
) -> OverpassResult:
    logging.info("⏬ Overpass Download")
    return _parseOverpassData(
        await _getOverpassHttpx(query=query, overpassUrl=overpassUrl)
    )
