#!/usr/bin/env python3
"""
Simple Flask application for testing CloudRun automation.
Provides /health and /hello-world endpoints.
"""

from flask import Flask, jsonify
import os
from datetime import datetime, UTC

app = Flask(__name__)


@app.route("/health")
def health():
    """Health check endpoint for load balancer and monitoring"""
    return (
        jsonify(
            {
                "status": "healthy",
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "helloworld-flask",
                "version": "1.0.0",
            }
        ),
        200,
    )


@app.route("/hello-world")
def hello_world():
    """Main application endpoint"""
    return (
        jsonify(
            {
                "message": "Hello, World from InfraDSL CloudRun!",
                "timestamp": datetime.now(UTC).isoformat(),
                "service": "helloworld-flask",
                "container_id": os.environ.get("HOSTNAME", "local"),
                "port": os.environ.get("PORT", "8080"),
            }
        ),
        200,
    )


@app.route("/")
def root():
    """Root endpoint redirects to hello-world"""
    return (
        jsonify(
            {
                "endpoints": {"health": "/health", "hello": "/hello-world"},
                "service": "helloworld-flask",
            }
        ),
        200,
    )


if __name__ == "__main__":
    # Cloud Run will set the PORT environment variable
    port = int(os.environ.get("PORT", 8080))
    print(f"Starting Flask app on 0.0.0.0:{port}")
    app.run(debug=False, host="0.0.0.0", port=port)
# Test change
