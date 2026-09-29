"""Tests unitaires pour `triangulator.triangles.Triangles` (voir PLAN.md, section 2)."""

import struct

import pytest

from triangulator.point_set import PointSet
from triangulator.triangles import InvalidTriangleIndexError, Triangles


def _pack_points(points):
    """Construit un buffer PointSet à la main, sans passer par encode()."""
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
    """Teste qu'encoder puis décoder un Triangles préserve sommets et triangles."""
    vertices = PointSet(points=((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)))
    triangle_indices = ((0, 1, 2),)
    triangles = Triangles(vertices=vertices, triangle_indices=triangle_indices)

    decoded = Triangles.decode(triangles.encode())

    assert decoded.vertices.points == vertices.points
    assert decoded.triangle_indices == triangle_indices


def test_decode_with_no_triangles_returns_empty_triangle_list():
    """Teste que des sommets avec 0 triangle se décodent en une liste vide."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    decoded = Triangles.decode(_pack_triangles(points, []))

    assert decoded.vertices.points == tuple(points)
    assert decoded.triangle_indices == ()


def test_triangle_referencing_unknown_vertex_index_raises():
    """Teste qu'un indice de triangle hors de la liste des sommets est rejeté."""
    vertices = PointSet(points=((0.0, 0.0), (1.0, 0.0), (0.0, 1.0)))

    with pytest.raises(InvalidTriangleIndexError):
        Triangles(vertices=vertices, triangle_indices=((0, 1, 5),))
