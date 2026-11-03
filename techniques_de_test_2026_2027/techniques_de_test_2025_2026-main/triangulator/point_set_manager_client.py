"""Récupère un PointSet auprès du service PointSetManager, en HTTP."""


def fetch_point_set(
    base_url: str, point_set_id: str, timeout: float = 5.0
) -> tuple[int, bytes]:
    """Appelle GET {base_url}/pointset/{point_set_id}.

    Renvoie (code_http, corps), y compris pour un code d'erreur (404,
    500...). Lève OSError si le service est injoignable ou trop lent.
    """
    raise NotImplementedError
