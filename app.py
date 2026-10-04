"""Entry point.  Run locally with:   python app.py
Production:                         gunicorn "app:create_app()"
"""
import logging

from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import HTTPException

from routes.bst_routes import bst_bp
from routes.generate_routes import generate_bp
from routes.graph_routes import graph_bp
from routes.heap_routes import heap_bp
from routes.queue_routes import queue_bp
from routes.reference_routes import reference_bp
from routes.stack_routes import stack_bp


def create_app():
    app = Flask(__name__)

    for bp in (bst_bp, graph_bp, heap_bp, stack_bp, queue_bp, generate_bp, reference_bp):
        app.register_blueprint(bp)

    @app.get("/")
    def index():
        return render_template("index.html")

    @app.errorhandler(Exception)
    def handle_unexpected(exc):
        # Invalid input must never crash the app: always answer API calls with JSON.
        if isinstance(exc, HTTPException):
            if request.path.startswith("/api/"):
                return jsonify({"error": exc.description}), exc.code
            return exc
        logging.exception("Unhandled error")
        return jsonify({"error": "Something went wrong on the server"}), 500

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
