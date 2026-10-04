from flask import Blueprint

from routes._util import json_endpoint
from services import generate_service

generate_bp = Blueprint("generate", __name__, url_prefix="/api")

generate_bp.add_url_rule("/generate", "generate", json_endpoint(generate_service.generate), methods=["POST"])
