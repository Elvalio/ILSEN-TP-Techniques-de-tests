"""Tests de performance pour la triangulation et l'encodage/décodage binaire.

Voir PLAN.md, section 6. Ce ne sont pas des tests de correction stricts
pass/fail : ils rapportent des temps et utilisent des plafonds larges,
juste pour détecter une régression de performance catastrophique. Lancés
seuls via `make perf_test` ; exclus de `make unit_test`.
"""

import random
import time

import pytest

from triangulator.point_set import PointSet
from triangulator.triangles import Triangles
from triangulator.triangulation import triangulate

pytestmark = pytest.mark.perf


def _random_points(count: int) -> tuple[tuple[float, float], ...]:
    """Génère `count` points 2D pseudo-aléatoires, avec une graine reproductible."""
    rng = random.Random(42)
    return tuple(
        (rng.uniform(-1000, 1000), rng.uniform(-1000, 1000)) for _ in range(count)
    )


@pytest.mark.parametrize("point_count", [1_000, 10_000])
def test_triangulation_duration(point_count: int):
    """Rapporte et vérifie le temps de triangulation d'un grand PointSet."""
    point_set = PointSet(points=_random_points(point_count))

    start = time.perf_counter()
    triangulate(point_set)
    elapsed = time.perf_counter() - start

    print(f"\n[perf] triangulate({point_count} points): {elapsed:.3f}s")
    assert elapsed < 30.0


@pytest.mark.parametrize("point_count", [1_000, 10_000, 100_000])
def test_point_set_encode_decode_duration(point_count: int):
    """Rapporte et vérifie sommairement le temps d'encodage/décodage de PointSet."""
    point_set = PointSet(points=_random_points(point_count))

    start = time.perf_counter()
    encoded = point_set.encode()
    encode_time = time.perf_counter() - start

    start = time.perf_counter()
    PointSet.decode(encoded)
    decode_time = time.perf_counter() - start

    print(
        f"\n[perf] PointSet encode/decode ({point_count} points): "
        f"encode={encode_time:.3f}s decode={decode_time:.3f}s"
    )
    assert encode_time < 10.0
    assert decode_time < 10.0


@pytest.mark.parametrize("point_count", [1_000, 10_000])
def test_triangles_encode_decode_duration(point_count: int):
    """Rapporte et vérifie sommairement le temps d'encodage/décodage de Triangles."""
    points = _random_points(point_count)
    triangle_indices = tuple(
        (i, (i + 1) % point_count, (i + 2) % point_count) for i in range(point_count)
    )
    vertices = PointSet(points=points)
    triangles = Triangles(vertices=vertices, triangle_indices=triangle_indices)

    start = time.perf_counter()
    encoded = triangles.encode()
    encode_time = time.perf_counter() - start

    start = time.perf_counter()
    Triangles.decode(encoded)
    decode_time = time.perf_counter() - start

    print(
        f"\n[perf] Triangles encode/decode ({point_count} points/triangles): "
        f"encode={encode_time:.3f}s decode={decode_time:.3f}s"
    )
    assert encode_time < 10.0
    assert decode_time < 10.0
