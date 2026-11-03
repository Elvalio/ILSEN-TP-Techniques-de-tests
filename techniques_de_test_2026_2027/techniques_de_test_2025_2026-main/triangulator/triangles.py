"""Encode/décode le format binaire Triangles (voir PLAN.md, section 2).

Format binaire :
- Les sommets, encodés exactement comme un PointSet.
- 4 octets (unsigned long, little-endian) : nombre de triangles T.
- T * 12 octets : les triangles, chacun sous forme de 3 unsigned longs
  little-endian référençant des indices de sommets.
"""

from triangulator.point_set import Point

Triangle = tuple[int, int, int]


def encode_triangles(points: list[Point], triangles: list[Triangle]) -> bytes:
    """Encode des sommets et des triangles vers le format binaire Triangles.

    Lève ValueError si un triangle référence un indice de sommet absent
    de points.
    """
    raise NotImplementedError


def decode_triangles(data: bytes) -> tuple[list[Point], list[Triangle]]:
    """Décode un buffer binaire Triangles. Lève ValueError si invalide."""
    raise NotImplementedError
