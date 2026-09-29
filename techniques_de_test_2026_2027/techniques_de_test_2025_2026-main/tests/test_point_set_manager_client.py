"""Tests pour PointSetManagerClient, avec urlopen mocké (voir PLAN.md, section 4).

On patche urllib.request.urlopen directement : l'implémentation doit donc
l'appeler via `urllib.request.urlopen(...)`, pas via un import direct
(`from urllib.request import urlopen`), sinon le mock ne prend pas la main.
"""

import io
import struct
from unittest.mock import patch
from urllib.error import HTTPError, URLError

import pytest

from triangulator.point_set import PointSetDecodingError
from triangulator.point_set_manager_client import (
    PointSetManagerClient,
    PointSetManagerUnavailableError,
    PointSetNotFoundError,
)

POINT_SET_ID = "123e4567-e89b-12d3-a456-426614174000"
BASE_URL = "http://point-set-manager.example"


def _pack_points(points):
    """Construit un buffer PointSet à la main, sans passer par encode()."""
    data = struct.pack("<L", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


@pytest.fixture
def mock_urlopen():
    """Remplace urlopen() par un mock pendant le temps du test."""
    with patch("urllib.request.urlopen") as mock:
        yield mock


def test_get_point_set_calls_the_expected_url(mock_urlopen):
    """La requête doit partir sur /pointset/{id}, avec le bon id."""
    mock_urlopen.return_value = io.BytesIO(_pack_points([(1.0, 2.0)]))
    client = PointSetManagerClient(base_url=BASE_URL)

    client.get_point_set(POINT_SET_ID)

    called_url = mock_urlopen.call_args[0][0]
    assert called_url == f"{BASE_URL}/pointset/{POINT_SET_ID}"


def test_get_point_set_returns_the_decoded_point_set(mock_urlopen):
    """Le PointSet renvoyé doit correspondre à ce que urlopen a répondu."""
    mock_urlopen.return_value = io.BytesIO(_pack_points([(1.0, 2.0)]))
    client = PointSetManagerClient(base_url=BASE_URL)

    point_set = client.get_point_set(POINT_SET_ID)

    assert point_set.points == ((1.0, 2.0),)


def test_unknown_id_raises_not_found(mock_urlopen):
    """Un 404 du PointSetManager doit devenir un PointSetNotFoundError."""
    mock_urlopen.side_effect = HTTPError(BASE_URL, 404, "Not Found", None, None)
    client = PointSetManagerClient(base_url=BASE_URL)

    with pytest.raises(PointSetNotFoundError):
        client.get_point_set(POINT_SET_ID)


def test_unreachable_service_raises_unavailable(mock_urlopen):
    """Si la connexion échoue, on doit avoir un PointSetManagerUnavailableError."""
    mock_urlopen.side_effect = URLError(ConnectionRefusedError())
    client = PointSetManagerClient(base_url=BASE_URL)

    with pytest.raises(PointSetManagerUnavailableError):
        client.get_point_set(POINT_SET_ID)


def test_timeout_raises_unavailable(mock_urlopen):
    """Même chose si la requête dépasse le timeout."""
    mock_urlopen.side_effect = TimeoutError()
    client = PointSetManagerClient(base_url=BASE_URL, timeout=0.2)

    with pytest.raises(PointSetManagerUnavailableError):
        client.get_point_set(POINT_SET_ID)


def test_corrupted_response_body_raises_point_set_decoding_error(mock_urlopen):
    """Un corps de réponse illisible doit lever PointSetDecodingError."""
    mock_urlopen.return_value = io.BytesIO(b"\x03\x00\x00\x00")
    client = PointSetManagerClient(base_url=BASE_URL)

    with pytest.raises(PointSetDecodingError):
        client.get_point_set(POINT_SET_ID)


def test_unexpected_400_response_raises_unavailable(mock_urlopen):
    """Un 400 inattendu (cas documenté dans PLAN.md) est traité comme indisponible."""
    mock_urlopen.side_effect = HTTPError(BASE_URL, 400, "Bad Request", None, None)
    client = PointSetManagerClient(base_url=BASE_URL)

    with pytest.raises(PointSetManagerUnavailableError):
        client.get_point_set(POINT_SET_ID)
