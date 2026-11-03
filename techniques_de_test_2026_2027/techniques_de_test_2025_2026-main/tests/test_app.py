"""Tests bout en bout pour `GET /triangulation/{pointSetId}` (voir PLAN.md, section 5).

Le PointSetManager est simulé par un mock injecté comme fetch_point_set,
donc aucun vrai appel HTTP n'a lieu ; décodage, triangulation et
encodage sont, eux, réellement exercés.
"""

import struct
from unittest.mock import Mock

import pytest

from triangulator.app import create_app
from triangulator.triangles import decode_triangles

KNOWN_ID = "123e4567-e89b-12d3-a456-426614174000"
UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"


def _pack_points(points):
    """Construit un buffer PointSet à la main."""
    data = struct.pack("<L", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


def test_success_returns_binary_triangles():
    """Teste qu'un pointSetId valide et connu renvoie un corps Triangles décodable."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    manager = Mock(return_value=(200, _pack_points(points)))
    client = create_app(manager).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 200
    assert response.content_type == "application/octet-stream"
    manager.assert_called_once_with(KNOWN_ID)

    decoded_points, decoded_triangles = decode_triangles(response.data)
    assert len(decoded_triangles) >= 1
    assert set(decoded_points) == set(points)


def test_malformed_point_set_id_returns_400():
    """Teste qu'un pointSetId non-UUID est rejeté sans jamais appeler le manager."""
    manager = Mock()
    client = create_app(manager).test_client()

    response = client.get("/triangulation/abc")

    assert response.status_code == 400
    assert response.json == {
        "code": "INVALID_POINT_SET_ID",
        "message": "'abc' is not a valid pointSetId (expected a UUID).",
    }
    manager.assert_not_called()


def test_unknown_point_set_id_returns_404():
    """Teste qu'un id inconnu du PointSetManager (404) renvoie NOT_FOUND."""
    manager = Mock(return_value=(404, b""))
    client = create_app(manager).test_client()

    response = client.get(f"/triangulation/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json == {
        "code": "NOT_FOUND",
        "message": f"No PointSet found for id '{UNKNOWN_ID}'.",
    }


@pytest.mark.parametrize("manager_status", [400, 500, 503])
def test_unexpected_manager_status_returns_503(manager_status: int):
    """Teste qu'un statut inattendu du PointSetManager est traité comme indisponible."""
    manager = Mock(return_value=(manager_status, b""))
    client = create_app(manager).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 503
    assert response.json == {
        "code": "POINT_SET_MANAGER_UNAVAILABLE",
        "message": "Could not reach the PointSetManager service.",
    }


def test_manager_unreachable_returns_503():
    """Teste qu'une panne réseau vers le PointSetManager renvoie 503."""
    manager = Mock(side_effect=OSError("panne réseau"))
    client = create_app(manager).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 503
    assert response.json == {
        "code": "POINT_SET_MANAGER_UNAVAILABLE",
        "message": "Could not reach the PointSetManager service.",
    }


def test_corrupt_point_set_from_manager_returns_500():
    """Teste qu'un corps PointSet corrompu venant du PointSetManager renvoie un 500."""
    manager = Mock(return_value=(200, b"\x05\x00\x00\x00"))
    client = create_app(manager).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 500
    assert response.json == {
        "code": "INVALID_POINT_SET_FORMAT",
        "message": "The PointSet returned by PointSetManager is not valid.",
    }


def test_triangulation_failure_returns_500():
    """Teste qu'un PointSet avec trop peu de points renvoie TRIANGULATION_FAILED."""
    manager = Mock(return_value=(200, _pack_points([(0.0, 0.0)])))
    client = create_app(manager).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 500
    assert response.json == {
        "code": "TRIANGULATION_FAILED",
        "message": "Triangulation could not be computed for the given point set.",
    }


def test_post_method_not_allowed():
    """Teste que seule la méthode GET est autorisée sur la route de triangulation."""
    client = create_app(Mock()).test_client()

    response = client.post(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 405


def test_unknown_route_returns_404():
    """Teste qu'une route inconnue ou un pointSetId vide renvoie 404."""
    client = create_app(Mock()).test_client()

    assert client.get("/triangulation/").status_code == 404
    assert client.get("/inconnu").status_code == 404
