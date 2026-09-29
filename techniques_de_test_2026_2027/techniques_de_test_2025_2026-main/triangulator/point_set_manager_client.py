"""Récupère des PointSets depuis le service HTTP PointSetManager."""

from triangulator.point_set import PointSet


class PointSetNotFoundError(Exception):
    """Levée quand le PointSetManager n'a pas de PointSet pour l'id demandé."""


class PointSetManagerUnavailableError(Exception):
    """Levée quand le PointSetManager est injoignable ou échoue de façon inattendue."""


class PointSetManagerClient:
    """Client pour l'API HTTP du PointSetManager."""

    def __init__(self, base_url: str, timeout: float = 5.0) -> None:
        """Configure l'URL de base du PointSetManager et le timeout par requête."""
        self.base_url = base_url
        self.timeout = timeout

    def get_point_set(self, point_set_id: str) -> PointSet:
        """Récupère et décode le PointSet identifié par point_set_id."""
        raise NotImplementedError
