import os
from flask import Flask
from .core import custom_render
from .loader import CustomHtmlLoader
from .errorhandling import init_error_handlers
import logging


logging.getLogger('flask.cli').disabled = True
logging.getLogger('werkzeug').disabled = True
print("Created By Raven Studio")

class VelraApp:
    def __init__(self, import_name, template_folder=None):
        # Determine template folder path
        if template_folder is None:
            template_folder = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

        # Create the Flask app with custom template folder
        self.app = Flask(import_name, template_folder=template_folder)

        # Use your custom HTML loader for templates
        self.app.jinja_loader = CustomHtmlLoader(template_folder)

        # Register your custom error handlers (404, 500, etc.)
        init_error_handlers(self.app)

    def route(self, *args, **kwargs):
        # Pass the route decorator directly to Flask's app
        return self.app.route(*args, **kwargs)

    def render(self, template_name, **context):
        # Use your custom render function for templates
        return custom_render(template_name, **context)

    def run(self, *args, **kwargs):
        # Run the Flask app
        self.app.run(*args, **kwargs)
