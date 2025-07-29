# velra/errorhandling.py

import traceback
from flask import jsonify, request

def register_error_handlers(app):
    # Catch all 404s
    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            "error": "Page Not Found",
            "code": 404,
            "path": request.path
        }), 404

    # Catch all 500s
    @app.errorhandler(500)
    def internal_error(error):
        return jsonify({
            "error": "Internal Server Error",
            "code": 500,
            "details": str(error),
            "traceback": traceback.format_exc()
        }), 500

    # Catch any other HTTP exception
    @app.errorhandler(Exception)
    def handle_exception(error):
        return jsonify({
            "error": str(error),
            "type": type(error).__name__,
            "traceback": traceback.format_exc()
        }), 500
