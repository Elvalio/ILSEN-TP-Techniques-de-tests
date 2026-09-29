"""Représente un ensemble ordonné de points 2D, encodable en binaire.

Format binaire :
- 4 octets (unsigned long, little-endian) : nombre de points N.
- N * 8 octets : les points, chacun sous forme de 2 floats little-endian (X puis Y).
"""

from __future__ import annotations

from dataclasses import dataclass


class PointSetDecodingError(Exception):
    """Levée quand un buffer binaire de PointSet est malformé, tronqué ou incohérent."""


@dataclass(frozen=True)
class PointSet:
    """Un ensemble ordonné de points 2D."""

    points: tuple[tuple[float, float], ...]

    def encode(self) -> bytes:
        """Encode ce PointSet vers sa représentation binaire."""
        raise NotImplementedError

    @staticmethod
    def decode(data: bytes) -> PointSet:
        """Décode un PointSet depuis sa représentation binaire."""
        raise NotImplementedError
