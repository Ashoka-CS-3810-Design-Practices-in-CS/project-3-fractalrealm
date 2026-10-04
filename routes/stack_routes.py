from flask import Blueprint

from routes._util import json_endpoint
from services import stack_service

stack_bp = Blueprint("stack", __name__, url_prefix="/api/stack")

stack_bp.add_url_rule("/push", "push", json_endpoint(stack_service.push), methods=["POST"])
stack_bp.add_url_rule("/pop", "pop", json_endpoint(stack_service.pop), methods=["POST"])
stack_bp.add_url_rule("/peek", "peek", json_endpoint(stack_service.peek), methods=["POST"])
stack_bp.add_url_rule("/is_empty", "is_empty", json_endpoint(stack_service.is_empty), methods=["POST"])
