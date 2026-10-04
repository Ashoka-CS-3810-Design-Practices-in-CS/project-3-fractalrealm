from flask import Blueprint

from routes._util import json_endpoint
from services import graph_service

graph_bp = Blueprint("graph", __name__, url_prefix="/api/graph")

graph_bp.add_url_rule("/add_vertex", "add_vertex", json_endpoint(graph_service.add_vertex), methods=["POST"])
graph_bp.add_url_rule("/remove_vertex", "remove_vertex", json_endpoint(graph_service.remove_vertex), methods=["POST"])
graph_bp.add_url_rule("/add_edge", "add_edge", json_endpoint(graph_service.add_edge), methods=["POST"])
graph_bp.add_url_rule("/remove_edge", "remove_edge", json_endpoint(graph_service.remove_edge), methods=["POST"])
graph_bp.add_url_rule("/bfs", "bfs", json_endpoint(graph_service.run_bfs), methods=["POST"])
graph_bp.add_url_rule("/dfs", "dfs", json_endpoint(graph_service.run_dfs), methods=["POST"])
graph_bp.add_url_rule("/compare", "compare", json_endpoint(graph_service.compare), methods=["POST"])
