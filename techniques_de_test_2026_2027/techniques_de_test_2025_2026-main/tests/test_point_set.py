"""Tests unitaires pour `triangulator.point_set.PointSet` (voir PLAN.md, section 1)."""

import struct

import pytest

from triangulator.point_set import PointSet, PointSetDecodingError


def _pack_points(points):
    """Construit un buffer PointSet à la main, sans passer par encode()."""
    data = struct.pack("<L", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


def test_round_trip_preserves_points_and_order():
    """Teste qu'encoder puis décoder un PointSet renvoie les mêmes points, en ordre."""
    points = ((0.0, 0.0), (1.5, -2.25), (3.125, 42.0))
    point_set = PointSet(points=points)

    decoded = PointSet.decode(point_set.encode())

    assert decoded.points == points


def test_decode_of_empty_point_set_returns_empty_list():
    """Teste que décoder un PointSet avec 0 point réussit et renvoie une liste vide."""
    decoded = PointSet.decode(_pack_points([]))

    assert decoded.points == ()


@pytest.mark.parametrize(
    "data",
    [
        pytest.param(b"", id="empty_buffer"),
        pytest.param(b"\x00\x00", id="fewer_than_4_bytes"),
        pytest.param(_pack_points([(1.0, 2.0)])[:-1], id="truncated_mid_point"),
    ],
)
def test_decode_of_too_short_buffer_raises(data: bytes):
    """Teste qu'un buffer plus court que son en-tête ou tronqué au milieu est rejeté."""
    with pytest.raises(PointSetDecodingError):
        PointSet.decode(data)


def test_decode_with_inconsistent_declared_size_raises():
    """Teste qu'un compte de points incohérent avec les octets restants échoue."""
    data = _pack_points([(1.0, 2.0), (3.0, 4.0)]) + b"\x00\x00\x00"

    with pytest.raises(PointSetDecodingError):
        PointSet.decode(data)
