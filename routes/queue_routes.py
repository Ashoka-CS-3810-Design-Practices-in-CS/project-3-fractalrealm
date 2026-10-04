from flask import Blueprint

from routes._util import json_endpoint
from services import queue_service

queue_bp = Blueprint("queue", __name__, url_prefix="/api/queue")

queue_bp.add_url_rule("/enqueue", "enqueue", json_endpoint(queue_service.enqueue), methods=["POST"])
queue_bp.add_url_rule("/dequeue", "dequeue", json_endpoint(queue_service.dequeue), methods=["POST"])
queue_bp.add_url_rule("/front", "front", json_endpoint(queue_service.front), methods=["POST"])
queue_bp.add_url_rule("/rear", "rear", json_endpoint(queue_service.rear), methods=["POST"])
queue_bp.add_url_rule("/is_empty", "is_empty", json_endpoint(queue_service.is_empty), methods=["POST"])
