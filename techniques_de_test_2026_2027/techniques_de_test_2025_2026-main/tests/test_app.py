"""Tests bout en bout pour `GET /triangulation/{pointSetId}` (voir PLAN.md, section 5).

Le PointSetManager est simulé en mockant directement `PointSetManagerClient`,
donc aucun vrai appel HTTP n'a lieu ; l'algorithme de triangulation et
l'encodage binaire sont, eux, réellement exercés.
"""

from unittest.mock import Mock

from triangulator.app import create_app
from triangulator.point_set import PointSet, PointSetDecodingError
from triangulator.point_set_manager_client import (
    PointSetManagerUnavailableError,
    PointSetNotFoundError,
)
from triangulator.triangles import Triangles

KNOWN_ID = "123e4567-e89b-12d3-a456-426614174000"
UNKNOWN_ID = "00000000-0000-0000-0000-000000000000"


def _client_returning(point_set: PointSet) -> Mock:
    """Construit un mock de PointSetManagerClient qui renvoie point_set."""
    mock_client = Mock()
    mock_client.get_point_set.return_value = point_set
    return mock_client


def _client_raising(exception: Exception) -> Mock:
    """Construit un mock de PointSetManagerClient dont get_point_set lève exception."""
    mock_client = Mock()
    mock_client.get_point_set.side_effect = exception
    return mock_client


def test_success_returns_binary_triangles():
    """Teste qu'un pointSetId valide et connu renvoie un corps Triangles décodable."""
    point_set = PointSet(points=((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)))
    client = create_app(_client_returning(point_set)).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 200
    assert response.content_type == "application/octet-stream"

    triangles = Triangles.decode(response.data)
    assert len(triangles.triangle_indices) >= 1
    assert set(triangles.vertices.points) == set(point_set.points)


def test_malformed_point_set_id_returns_400():
    """Teste qu'un pointSetId non-UUID est rejeté avec INVALID_POINT_SET_ID."""
    client = create_app(Mock()).test_client()

    response = client.get("/triangulation/abc")

    assert response.status_code == 400
    assert response.json == {
        "code": "INVALID_POINT_SET_ID",
        "message": "'abc' is not a valid pointSetId (expected a UUID).",
    }


def test_unknown_point_set_id_returns_404():
    """Teste qu'un id inconnu du PointSetManager renvoie NOT_FOUND."""
    client = create_app(_client_raising(PointSetNotFoundError())).test_client()

    response = client.get(f"/triangulation/{UNKNOWN_ID}")

    assert response.status_code == 404
    assert response.json == {
        "code": "NOT_FOUND",
        "message": f"No PointSet found for id '{UNKNOWN_ID}'.",
    }


def test_point_set_manager_unavailable_returns_503():
    """Teste qu'un PointSetManager injoignable renvoie une erreur 503."""
    mock_client = _client_raising(PointSetManagerUnavailableError())
    client = create_app(mock_client).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 503
    assert response.json == {
        "code": "POINT_SET_MANAGER_UNAVAILABLE",
        "message": "Could not reach the PointSetManager service.",
    }


def test_triangulation_failure_returns_500():
    """Teste qu'un PointSet avec trop peu de points renvoie TRIANGULATION_FAILED."""
    point_set = PointSet(points=((0.0, 0.0),))
    client = create_app(_client_returning(point_set)).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 500
    assert response.json == {
        "code": "TRIANGULATION_FAILED",
        "message": "Triangulation could not be computed for the given point set.",
    }


def test_corrupt_point_set_from_manager_returns_500():
    """Teste qu'un corps PointSet corrompu venant du PointSetManager renvoie un 500."""
    client = create_app(_client_raising(PointSetDecodingError())).test_client()

    response = client.get(f"/triangulation/{KNOWN_ID}")

    assert response.status_code == 500
    assert response.json == {
        "code": "INVALID_POINT_SET_FORMAT",
        "message": "The PointSet returned by PointSetManager is not valid.",
    }
