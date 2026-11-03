"""Tests de performance pour la triangulation et l'encodage/décodage binaire.

Voir PLAN.md, section 6. Ce ne sont pas des tests de correction stricts
pass/fail : ils rapportent des temps et utilisent des plafonds larges,
juste pour détecter une régression de performance catastrophique. Lancés
seuls via `make perf_test` ; exclus de `make unit_test`.
"""

import random
import statistics
import time

import pytest

from triangulator.point_set import decode_point_set, encode_point_set
from triangulator.triangles import decode_triangles, encode_triangles
from triangulator.triangulation import triangulate

pytestmark = pytest.mark.perf


def _random_points(count: int) -> list[tuple[float, float]]:
    """Génère `count` points 2D pseudo-aléatoires, avec une graine reproductible."""
    rng = random.Random(42)
    return [(rng.uniform(-1000, 1000), rng.uniform(-1000, 1000)) for _ in range(count)]


@pytest.mark.parametrize("point_count", [1_000, 10_000])
def test_triangulation_duration(point_count: int):
    """Rapporte et vérifie le temps de triangulation d'un grand PointSet."""
    points = _random_points(point_count)

    start = time.perf_counter()
    triangulate(points)
    elapsed = time.perf_counter() - start

    print(f"\n[perf] triangulate({point_count} points): {elapsed:.3f}s")
    assert elapsed < 30.0


def test_triangulation_time_does_not_explode_when_points_double():
    """Teste que le temps ne quadruple pas quand le nombre de points double."""
    durations = []
    for point_count in (1_000, 2_000, 4_000):
        points = _random_points(point_count)
        measures = []
        for _ in range(3):
            start = time.perf_counter()
            triangulate(points)
            measures.append(time.perf_counter() - start)
        durations.append(statistics.median(measures))

    print(f"\n[perf] évolution (1000/2000/4000 points): {durations}")
    assert durations[1] <= 4 * durations[0]
    assert durations[2] <= 4 * durations[1]


@pytest.mark.parametrize("point_count", [1_000, 10_000, 100_000])
def test_point_set_encode_decode_duration(point_count: int):
    """Rapporte et vérifie sommairement le temps d'encodage/décodage de PointSet."""
    points = _random_points(point_count)

    start = time.perf_counter()
    encoded = encode_point_set(points)
    encode_time = time.perf_counter() - start

    start = time.perf_counter()
    decode_point_set(encoded)
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
    triangle_indices = [
        (i, (i + 1) % point_count, (i + 2) % point_count) for i in range(point_count)
    ]

    start = time.perf_counter()
    encoded = encode_triangles(points, triangle_indices)
    encode_time = time.perf_counter() - start

    start = time.perf_counter()
    decode_triangles(encoded)
    decode_time = time.perf_counter() - start

    print(
        f"\n[perf] Triangles encode/decode ({point_count} points/triangles): "
        f"encode={encode_time:.3f}s decode={decode_time:.3f}s"
    )
    assert encode_time < 10.0
    assert decode_time < 10.0
