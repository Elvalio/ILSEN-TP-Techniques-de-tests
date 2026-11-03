"""Tests pour fetch_point_set, avec urlopen mocké (voir PLAN.md, section 4).

On patche urllib.request.urlopen directement : l'implémentation doit donc
l'appeler via `urllib.request.urlopen(...)` (`import urllib.request`, pas
`from urllib.request import urlopen`) pour que le patch s'applique.
"""

import io
import struct
from unittest.mock import Mock, patch
from urllib.error import HTTPError, URLError

import pytest

from triangulator.point_set_manager_client import fetch_point_set

POINT_SET_ID = "123e4567-e89b-12d3-a456-426614174000"
BASE_URL = "http://point-set-manager.example"


def _pack_points(points):
    """Construit un buffer PointSet à la main."""
    data = struct.pack("<L", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


def _fake_response(status, body):
    """Construit un faux objet réponse HTTP, comme celui que renvoie urlopen()."""
    response = Mock()
    response.status = status
    response.read.return_value = body
    response.__enter__ = Mock(return_value=response)
    response.__exit__ = Mock(return_value=False)
    return response


@pytest.fixture
def mock_urlopen():
    """Remplace urlopen() par un mock pendant le temps du test."""
    with patch("urllib.request.urlopen") as mock:
        yield mock


def test_fetch_point_set_calls_the_expected_url(mock_urlopen):
    """La requête doit partir sur /pointset/{id}, avec le bon id."""
    mock_urlopen.return_value = _fake_response(200, _pack_points([(1.0, 2.0)]))

    fetch_point_set(BASE_URL, POINT_SET_ID)

    called_url = mock_urlopen.call_args[0][0]
    assert called_url == f"{BASE_URL}/pointset/{POINT_SET_ID}"


def test_fetch_point_set_returns_status_and_body(mock_urlopen):
    """La fonction doit renvoyer (200, le corps reçu) en cas de succès."""
    body = _pack_points([(1.0, 2.0)])
    mock_urlopen.return_value = _fake_response(200, body)

    assert fetch_point_set(BASE_URL, POINT_SET_ID) == (200, body)


def test_fetch_point_set_returns_404_status(mock_urlopen):
    """Un 404 du PointSetManager doit être renvoyé tel quel, pas levé en exception."""
    mock_urlopen.side_effect = HTTPError(
        BASE_URL, 404, "Not Found", None, io.BytesIO(b"")
    )

    status, _ = fetch_point_set(BASE_URL, POINT_SET_ID)

    assert status == 404


def test_fetch_point_set_returns_500_status(mock_urlopen):
    """Un 500 (erreur interne du PointSetManager) doit aussi être renvoyé tel quel."""
    mock_urlopen.side_effect = HTTPError(
        BASE_URL, 500, "Internal Server Error", None, io.BytesIO(b"")
    )

    status, _ = fetch_point_set(BASE_URL, POINT_SET_ID)

    assert status == 500


def test_unreachable_service_raises_oserror(mock_urlopen):
    """Si la connexion échoue, l'erreur réseau doit remonter telle quelle."""
    mock_urlopen.side_effect = URLError(ConnectionRefusedError())

    with pytest.raises(OSError):
        fetch_point_set(BASE_URL, POINT_SET_ID)


def test_timeout_raises_oserror(mock_urlopen):
    """Même chose si la requête dépasse le timeout."""
    mock_urlopen.side_effect = TimeoutError()

    with pytest.raises(OSError):
        fetch_point_set(BASE_URL, POINT_SET_ID, timeout=0.2)
