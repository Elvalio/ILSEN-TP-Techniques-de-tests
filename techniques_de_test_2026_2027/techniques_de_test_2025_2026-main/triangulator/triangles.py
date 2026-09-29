"""Représente un résultat de triangulation, encodable en binaire.

Format binaire :
- Les sommets, encodés exactement comme un PointSet.
- 4 octets (unsigned long, little-endian) : nombre de triangles T.
- T * 12 octets : les triangles, chacun sous forme de 3 unsigned longs
  little-endian référençant des indices de sommets.
"""

from __future__ import annotations

from dataclasses import dataclass

from triangulator.point_set import PointSet


class InvalidTriangleIndexError(Exception):
    """Levée quand un triangle référence un indice de sommet hors de son PointSet."""


@dataclass(frozen=True)
class Triangles:
    """Un ensemble de sommets plus les triangles qui les relient, en triplets."""

    vertices: PointSet
    triangle_indices: tuple[tuple[int, int, int], ...]

    def encode(self) -> bytes:
        """Encode ce Triangles vers sa représentation binaire."""
        raise NotImplementedError

    @staticmethod
    def decode(data: bytes) -> Triangles:
        """Décode un Triangles depuis sa représentation binaire."""
        raise NotImplementedError
