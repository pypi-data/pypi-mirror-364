# velra/__init__.py
import os
from flask import Flask
from .core import custom_render
from .loader import CustomHtmlLoader
from .errorhandling import register_error_handlers  # Your custom error handler setup

class VelraApp:
    def __init__(self, import_name, template_folder=None):
        # Create Flask app with optional custom template folder
        if template_folder is None:
            template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

        self.app = Flask(import_name, template_folder=template_folder)

        # Use your custom HTML loader for templates
        self.app.jinja_loader = CustomHtmlLoader(template_folder)

        # Register custom error handlers (404, 500, etc.)
        register_error_handlers(self.app)

    def route(self, *args, **kwargs):
        # Pass route decorator to the underlying Flask app
        return self.app.route(*args, **kwargs)

    def render(self, template_name, **context):
        # Use your custom render function
        return custom_render(template_name, **context)

    def run(self, *args, **kwargs):
        # Run the Flask app
        self.app.run(*args, **kwargs)
