"""Tests unitaires pour l'encodage/décodage de Triangles (voir PLAN.md, section 2)."""

import struct

import pytest

from triangulator.triangles import decode_triangles, encode_triangles


def _pack_points(points):
    """Construit un buffer PointSet à la main, sans passer par encode_point_set()."""
    data = struct.pack("<L", len(points))
    for x, y in points:
        data += struct.pack("<ff", x, y)
    return data


def _pack_triangles(points, triangle_indices):
    """Construit un buffer Triangles à la main : sommets puis triangles."""
    data = _pack_points(points)
    data += struct.pack("<L", len(triangle_indices))
    for a, b, c in triangle_indices:
        data += struct.pack("<LLL", a, b, c)
    return data


def test_round_trip_preserves_vertices_and_triangles():
    """Teste qu'encoder puis décoder des triangles préserve sommets et triangles."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]
    triangle_indices = [(0, 1, 2)]

    decoded_points, decoded_triangles = decode_triangles(
        encode_triangles(points, triangle_indices)
    )

    assert decoded_points == points
    assert decoded_triangles == triangle_indices


def test_decode_with_no_triangles_returns_empty_triangle_list():
    """Teste que des sommets avec 0 triangle se décodent en une liste vide."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    decoded_points, decoded_triangles = decode_triangles(_pack_triangles(points, []))

    assert decoded_points == points
    assert decoded_triangles == []


def test_triangle_referencing_unknown_vertex_index_raises():
    """Teste qu'un indice de triangle hors de la liste des sommets est rejeté."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    with pytest.raises(ValueError):
        encode_triangles(points, [(0, 1, 5)])
