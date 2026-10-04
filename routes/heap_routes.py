from flask import Blueprint

from routes._util import json_endpoint
from services import heap_service

heap_bp = Blueprint("heap", __name__, url_prefix="/api/heap")

heap_bp.add_url_rule("/insert", "insert", json_endpoint(heap_service.insert), methods=["POST"])
heap_bp.add_url_rule("/extract_min", "extract_min", json_endpoint(heap_service.extract_min), methods=["POST"])
heap_bp.add_url_rule("/peek", "peek", json_endpoint(heap_service.peek), methods=["POST"])
