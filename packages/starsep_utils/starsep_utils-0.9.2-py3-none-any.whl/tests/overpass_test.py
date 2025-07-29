import pytest
from starsep_utils import (
    downloadOverpassData,
    RelationMember,
    Node,
    Relation,
    Way,
    OverpassResult,
    GeoPoint,
)

from starsep_utils.overpass import DEFAULT_OVERPASS_URL, KeyDict

expectedOverpassResult = OverpassResult(
    nodes={
        10001: Node(id=10001, type="node", tags=KeyDict({}), lat=52.01, lon=21.01),
        10002: Node(id=10002, type="node", tags=KeyDict({}), lat=52.02, lon=21.01),
        10003: Node(id=10003, type="node", tags=KeyDict({}), lat=52.03, lon=21.01),
        10004: Node(id=10004, type="node", tags=KeyDict({}), lat=52.04, lon=21.01),
        12345: Node(
            id=12345,
            type="node",
            tags=KeyDict({"amenity": "drinking_water"}),
            lat=52.01,
            lon=21.01,
        ),
    },
    ways={
        55555: Way(id=55555, type="way", tags=KeyDict({}), nodes=[10001, 10002, 10003]),
        66666: Way(id=66666, type="way", tags=KeyDict({}), nodes=[10002, 10003, 10004]),
        99999: Way(
            id=99999,
            type="way",
            tags=KeyDict({"amenity": "drinking_water", "building": "yes"}),
            nodes=[10001, 10002, 10003, 10004],
        ),
    },
    relations={
        111111: Relation(
            id=111111,
            type="relation",
            tags=KeyDict(
                {
                    "amenity": "drinking_water",
                    "building": "yes",
                    "man_made": "water_well",
                    "type": "multipolygon",
                }
            ),
            members=[
                RelationMember(type="way", id=55555, role="outer"),
                RelationMember(type="way", id=66666, role="outer"),
            ],
        )
    },
)


@pytest.mark.asyncio
async def testDownloadOverpassData(httpx_mock):
    httpx_mock.add_response(
        url=DEFAULT_OVERPASS_URL,
        json={
            "version": 0.6,
            "generator": "Overpass API 0.7.62.1 084b4234",
            "osm3s": {
                "timestamp_osm_base": "2024-07-07T08:48:16Z",
                "copyright": "The data included in this document is from www.openstreetmap.org. The data is made available under ODbL.",
            },
            "elements": [
                {
                    "type": "node",
                    "id": 12345,
                    "lat": 52.01,
                    "lon": 21.01,
                    "tags": {"amenity": "drinking_water"},
                },
                {"type": "node", "id": 10001, "lat": 52.01, "lon": 21.01},
                {"type": "node", "id": 10002, "lat": 52.02, "lon": 21.01},
                {"type": "node", "id": 10003, "lat": 52.03, "lon": 21.01},
                {"type": "node", "id": 10004, "lat": 52.04, "lon": 21.01},
                {
                    "type": "way",
                    "id": 99999,
                    "nodes": [10001, 10002, 10003, 10004],
                    "tags": {"amenity": "drinking_water", "building": "yes"},
                },
                {
                    "type": "way",
                    "id": 55555,
                    "nodes": [10001, 10002, 10003],
                },
                {
                    "type": "way",
                    "id": 66666,
                    "nodes": [10002, 10003, 10004],
                },
                {
                    "type": "relation",
                    "id": 111111,
                    "members": [
                        {"type": "way", "ref": 55555, "role": "outer"},
                        {"type": "way", "ref": 66666, "role": "outer"},
                    ],
                    "tags": {
                        "amenity": "drinking_water",
                        "building": "yes",
                        "man_made": "water_well",
                        "type": "multipolygon",
                    },
                },
            ],
        },
    )
    query = """
    nwr[amenity=drinking_water](52,21,52.1,21.1);
    (._;>;);
    out;
    """

    assert await downloadOverpassData(query) == expectedOverpassResult


def testCenter():
    assert expectedOverpassResult.nodes[12345].center(
        expectedOverpassResult
    ) == GeoPoint(lat=52.01, lon=21.01)
    assert expectedOverpassResult.ways[55555].center(
        expectedOverpassResult
    ) == GeoPoint(lat=52.02, lon=21.01)


def testBbox():
    assert expectedOverpassResult.nodes[12345].bbox(expectedOverpassResult) == (
        GeoPoint(lat=52.01, lon=21.01),
        GeoPoint(lat=52.01, lon=21.01),
    )
    assert expectedOverpassResult.ways[55555].bbox(expectedOverpassResult) == (
        GeoPoint(lat=52.01, lon=21.01),
        GeoPoint(lat=52.03, lon=21.01),
    )
    assert expectedOverpassResult.relations[111111].bbox(expectedOverpassResult) == (
        GeoPoint(lat=52.01, lon=21.01),
        GeoPoint(lat=52.04, lon=21.01),
    )
