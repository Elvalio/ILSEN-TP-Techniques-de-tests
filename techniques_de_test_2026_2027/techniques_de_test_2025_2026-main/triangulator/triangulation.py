"""Calcule la triangulation d'un PointSet."""

from triangulator.point_set import PointSet
from triangulator.triangles import Triangles


class TriangulationError(Exception):
    """Levée quand aucune triangulation valide n'existe pour un PointSet."""


def triangulate(point_set: PointSet) -> Triangles:
    """Renvoie la triangulation calculée pour le PointSet donné."""
    raise NotImplementedError
