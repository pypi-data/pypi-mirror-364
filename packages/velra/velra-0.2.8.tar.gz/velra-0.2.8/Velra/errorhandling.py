import traceback
from flask import request, render_template, current_app

def init_error_handlers(app):
    @app.errorhandler(404)
    def not_found(error):
        # Just print simple error message, no full stack trace
        print(f"ERROR 404: Path {request.path} not found.")

        # Return your custom 404 page or a simple message
        return render_template("404.html", path=request.path), 404

    @app.errorhandler(Exception)
    def internal_error(error):
        code = getattr(error, 'code', None)
        if code and code < 500:
            # Client errors (like 400, 403, 404) get simple log
            print(f"ERROR {code}: {request.path} caused error: {error}")
            return render_template(f"{code}.html", path=request.path), code

        # Server errors 500+ get full traceback
        print(f"ERROR {code or '500'}: Internal server error at path {request.path}")
        traceback.print_exc()

        return render_template("500.html"), 500
