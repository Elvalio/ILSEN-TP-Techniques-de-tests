"""Expose l'API HTTP du Triangulator décrite dans `api/triangulator.yml`."""

from flask import Flask

from triangulator.point_set_manager_client import PointSetManagerClient


class InvalidPointSetIdError(Exception):
    """Levée quand le paramètre pointSetId de l'URL n'est pas un UUID valide."""


def create_app(point_set_manager_client: PointSetManagerClient) -> Flask:
    """Construit l'app Flask du Triangulator, connectée au client PointSetManager."""
    app = Flask(__name__)

    @app.get("/triangulation/<point_set_id>")
    def get_triangulation(point_set_id: str):
        """Renvoie le Triangles binaire calculé pour le pointSetId donné."""
        raise NotImplementedError

    return app
