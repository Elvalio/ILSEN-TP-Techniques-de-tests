"""Calcule la triangulation d'un ensemble de points (voir PLAN.md, section 3)."""

from triangulator.point_set import Point
from triangulator.triangles import Triangle


def triangulate(points: list[Point]) -> list[Triangle]:
    """Renvoie les triangles (indices dans points) qui couvrent la surface.

    Lève ValueError si points ne peut pas être triangulé (pas assez de
    points, points alignés, points dupliqués).
    """
    raise NotImplementedError
