"""Encode/décode le format binaire PointSet (voir PLAN.md, section 1).

Format binaire :
- 4 octets (unsigned long, little-endian) : nombre de points N.
- N * 8 octets : les points, chacun sous forme de 2 floats (X puis Y).
"""

Point = tuple[float, float]


def encode_point_set(points: list[Point]) -> bytes:
    """Encode une liste de points vers le format binaire PointSet."""
    raise NotImplementedError


def decode_point_set(data: bytes) -> list[Point]:
    """Décode un buffer binaire PointSet. Lève ValueError si le buffer est invalide."""
    raise NotImplementedError
