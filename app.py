"""
Flask Application Entry Point
Accident Severity & Hospital Recommendation System
"""

import os
from flask import Flask, render_template, send_from_directory

from config import UPLOAD_FOLDER, MAX_CONTENT_LENGTH
from routes.analyze import analyze_bp
from routes.hospitals import hospitals_bp


def create_app() -> Flask:
    app = Flask(__name__)
    app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH
    app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
    app.secret_key = os.urandom(24)

    # Register blueprints
    app.register_blueprint(analyze_bp)
    app.register_blueprint(hospitals_bp)

    @app.route("/")
    def index():
        return render_template("index.html")

    @app.route("/uploads/<filename>")
    def uploaded_file(filename):
        return send_from_directory(UPLOAD_FOLDER, filename)

    return app


if __name__ == "__main__":
    # Ensure DB is seeded
    from database.setup_db import setup
    setup()

    app = create_app()
    print("\n🚑  Accident Severity & Hospital Recommendation System")
    print("🌐  Running at: http://127.0.0.1:5050\n")
    app.run(debug=True, host="0.0.0.0", port=5050)
