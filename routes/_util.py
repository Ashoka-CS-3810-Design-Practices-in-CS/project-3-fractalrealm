"""Small decorator shared by every route module."""
from functools import wraps

from flask import jsonify, request

from errors import VisualizerError


def json_endpoint(service_fn):
    """Parse the JSON body, call the service function, return JSON.

    Expected failures (VisualizerError) become ``{"error": "..."}`` with HTTP 400;
    the structure the browser holds is never touched by the server.
    """
    @wraps(service_fn)
    def wrapper():
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify({"error": "Request body must be a JSON object"}), 400
        try:
            return jsonify(service_fn(payload))
        except VisualizerError as exc:
            return jsonify({"error": str(exc)}), 400

    return wrapper
