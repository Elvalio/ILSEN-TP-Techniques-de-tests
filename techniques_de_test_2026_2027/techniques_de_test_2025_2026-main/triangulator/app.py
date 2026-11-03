"""Expose l'API HTTP du Triangulator décrite dans `api/triangulator.yml`."""

from collections.abc import Callable

from flask import Flask

FetchPointSet = Callable[[str], tuple[int, bytes]]


def create_app(fetch_point_set: FetchPointSet) -> Flask:
    """Construit l'app Flask, reliée à fetch_point_set pour obtenir les PointSets."""
    app = Flask(__name__)

    @app.get("/triangulation/<point_set_id>")
    def get_triangulation(point_set_id: str):
        """Renvoie le Triangles binaire calculé pour le pointSetId donné."""
        raise NotImplementedError

    return app
