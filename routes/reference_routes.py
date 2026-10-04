"""GET /api/reference: complexity + pseudocode for every operation, so the browser can show
the complexity panel as soon as an operation is selected (before it is run)."""
from flask import Blueprint, jsonify

from services.complexity import COMPLEXITY
from services.pseudocode import PSEUDOCODE

reference_bp = Blueprint("reference", __name__, url_prefix="/api")


@reference_bp.get("/reference")
def reference():
    return jsonify({"complexity": COMPLEXITY, "pseudocode": PSEUDOCODE})
