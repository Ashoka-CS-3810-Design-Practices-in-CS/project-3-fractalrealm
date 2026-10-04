from flask import Blueprint

from routes._util import json_endpoint
from services import bst_service

bst_bp = Blueprint("bst", __name__, url_prefix="/api/bst")

bst_bp.add_url_rule("/insert", "insert", json_endpoint(bst_service.insert), methods=["POST"])
bst_bp.add_url_rule("/delete", "delete", json_endpoint(bst_service.delete), methods=["POST"])
bst_bp.add_url_rule("/search", "search", json_endpoint(bst_service.search), methods=["POST"])
bst_bp.add_url_rule("/traverse", "traverse", json_endpoint(bst_service.traverse), methods=["POST"])
