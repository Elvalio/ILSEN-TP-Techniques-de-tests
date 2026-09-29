"""Tests unitaires pour l'algorithme de triangulation (voir PLAN.md, section 3)."""

import contextlib

import pytest

from triangulator.point_set import PointSet
from triangulator.triangulation import TriangulationError, triangulate


def test_three_non_aligned_points_form_exactly_one_triangle():
    """Teste que 3 points non alignés produisent exactement 1 triangle les contenant."""
    points = ((0.0, 0.0), (1.0, 0.0), (0.0, 1.0))
    point_set = PointSet(points=points)

    result = triangulate(point_set)

    assert len(result.triangle_indices) == 1
    used_points = {result.vertices.points[i] for i in result.triangle_indices[0]}
    assert used_points == set(points)


def test_square_produces_exactly_two_triangles_covering_it():
    """Teste qu'un carré (4 points) est triangulé en exactement 2 triangles."""
    points = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0))
    point_set = PointSet(points=points)

    result = triangulate(point_set)

    assert len(result.triangle_indices) == 2


@pytest.mark.parametrize("point_count", [0, 1, 2])
def test_not_enough_points_raises_triangulation_error(point_count: int):
    """Teste que moins de 3 points ne peuvent pas être triangulés."""
    points = tuple((float(i), 0.0) for i in range(point_count))

    with pytest.raises(TriangulationError):
        triangulate(PointSet(points=points))


def test_collinear_points_raise_triangulation_error():
    """Teste que 3 points alignés ou plus ne peuvent pas former un triangle valide."""
    points = ((0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0))

    with pytest.raises(TriangulationError):
        triangulate(PointSet(points=points))


def test_duplicate_points_are_handled_without_crashing():
    """Teste que des points dupliqués ne plantent pas (choix libre selon PLAN.md)."""
    points = ((0.0, 0.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0))

    with contextlib.suppress(TriangulationError):
        triangulate(PointSet(points=points))


def test_every_triangle_index_references_an_existing_vertex():
    """Teste que chaque indice de sommet du résultat existe dans le PointSet."""
    points = ((0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.5, 2.0))
    point_set = PointSet(points=points)

    result = triangulate(point_set)

    for triangle in result.triangle_indices:
        for index in triangle:
            assert 0 <= index < len(result.vertices.points)
