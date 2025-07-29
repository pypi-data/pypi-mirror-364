import traceback
from flask import request, current_app, render_template

def register_error_handlers(app):
    # Handle 404 errors
    @app.errorhandler(404)
    def not_found(error):
        # Log full traceback in terminal for debugging
        print(f"ERROR 404: Path {request.path} not found.")
        if current_app.debug:
            traceback.print_stack()
        
        # If you have custom generation logic for missing templates,
        # decide here if this is a "real" error or not.
        # Example: if request.path matches a pattern of custom generated pages, return that
        # Otherwise, render your custom 404 page.

        # For simplicity, serve a custom HTML template for 404:
        return render_template("404.html", path=request.path), 404

    # Handle 500 errors
    @app.errorhandler(500)
    def internal_error(error):
        # Print detailed traceback to terminal
        print(f"ERROR 500: Internal server error at {request.path}")
        traceback.print_exc()
        
        # Serve a friendly error page in browser
        return render_template("500.html", error=error), 500

    # Optionally, handle other HTTP errors or exceptions similarly

