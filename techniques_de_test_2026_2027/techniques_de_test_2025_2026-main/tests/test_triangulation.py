"""Tests unitaires pour l'algorithme de triangulation (voir PLAN.md, section 3)."""

import pytest

from triangulator.triangulation import triangulate


def test_three_non_aligned_points_form_exactly_one_triangle():
    """Teste que 3 points non alignés produisent exactement 1 triangle les contenant."""
    points = [(0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    triangles = triangulate(points)

    assert len(triangles) == 1
    used_points = {points[i] for i in triangles[0]}
    assert used_points == set(points)


def test_square_produces_exactly_two_triangles_covering_it():
    """Teste qu'un carré (4 points) est triangulé en exactement 2 triangles."""
    points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0)]

    assert len(triangulate(points)) == 2


@pytest.mark.parametrize("point_count", [0, 1, 2])
def test_not_enough_points_raises_value_error(point_count: int):
    """Teste que moins de 3 points ne peuvent pas être triangulés."""
    points = [(float(i), 0.0) for i in range(point_count)]

    with pytest.raises(ValueError):
        triangulate(points)


def test_collinear_points_raise_value_error():
    """Teste que 3 points alignés ou plus ne peuvent pas former un triangle valide."""
    points = [(0.0, 0.0), (1.0, 0.0), (2.0, 0.0), (3.0, 0.0)]

    with pytest.raises(ValueError):
        triangulate(points)


def test_duplicate_points_raise_value_error():
    """Teste qu'un point dupliqué est refusé (il donnerait un triangle d'aire nulle)."""
    points = [(0.0, 0.0), (0.0, 0.0), (1.0, 0.0), (0.0, 1.0)]

    with pytest.raises(ValueError):
        triangulate(points)


def test_every_triangle_index_references_an_existing_vertex():
    """Teste que chaque indice de sommet du résultat existe dans points."""
    points = [(0.0, 0.0), (1.0, 0.0), (1.0, 1.0), (0.0, 1.0), (0.5, 2.0)]

    triangles = triangulate(points)

    for triangle in triangles:
        for index in triangle:
            assert 0 <= index < len(points)
