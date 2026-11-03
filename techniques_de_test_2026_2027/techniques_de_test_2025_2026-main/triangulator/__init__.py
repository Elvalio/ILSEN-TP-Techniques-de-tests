"""Triangule des ensembles de points 2D et expose le résultat en HTTP."""

from triangulator.app import create_app
from triangulator.point_set import decode_point_set, encode_point_set
from triangulator.point_set_manager_client import fetch_point_set
from triangulator.triangles import decode_triangles, encode_triangles
from triangulator.triangulation import triangulate

__all__ = [
    "create_app",
    "decode_point_set",
    "decode_triangles",
    "encode_point_set",
    "encode_triangles",
    "fetch_point_set",
    "triangulate",
]
