# your_test_app/velra_library/init.py
from flask import Flask
from .core import custom_render
from .loader import CustomHtmlLoader
import os # Import os for path manipulation
import logging


logging.getLogger('flask.cli').disabled = True


class VelraApp:
    def __init__(self, import_name, template_folder=None): # Added template_folder argument
        self.app = Flask(import_name)

        # Determine the template folder path
        # If template_folder is not provided, default to 'templates' relative to app's root
        if template_folder is None:
            # This assumes 'templates' folder is a sibling of the app's root module
            # For example, if app.py is in 'your_test_app', and templates is also in 'your_test_app'
            template_folder = os.path.join(self.app.root_path, 'templates')

        # Use your custom HTML loader, passing the template folder to it
        self.app.jinja_loader = CustomHtmlLoader(template_folder)
        print(f"DEBUG: VelraApp initialized with template folder: {template_folder}")

        self._setup_routes()
    print("Created By Raven Studio")

    def _setup_routes(self):
        # The original home route from VelraApp, now using self.render
        @self.app.route('/velra-home') # Changed to '/velra-home' to avoid conflict with main.py's '/'
        def velra_home(): # Renamed the function to avoid conflict
            print("DEBUG: Accessing VelraApp's internal home route.")
            # This will use your custom loader and custom render, even if the template doesn't exist as a file
            return self.render("velra_default_page")

    def render(self, template_name, **context):
        # Use your custom render function here
        return custom_render(template_name, **context)

    def route(self, *args, **kwargs):
        # Pass through the Flask app's route decorator
        return self.app.route(*args, **kwargs)

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)
