# your_test_app/velra_library/init.py
from flask import Flask
from .core import custom_render
from .loader import CustomHtmlLoader
import os # Import os for path manipulation
import logging
from .errorhandling import register_error_handlers


logging.getLogger('flask.cli').disabled = True
logging.getLogger('werkzeug').disabled = True
print("Created By Raven Studio")

class VelraApp:
    def __init__(self, import_name, template_folder=None):
        self.app = Flask(import_name)
        register_error_handlers(self.app)
        # Determine the template folder path
        if template_folder is None:
            template_folder = os.path.join(self.app.root_path, 'templates')

        # Use your custom HTML loader, passing the template folder to it
        self.app.jinja_loader = CustomHtmlLoader(template_folder)
        print(f"DEBUG: VelraApp initialized with template folder: {template_folder}")

        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/velra-home')
        def velra_home():
            print("DEBUG: Accessing VelraApp's internal home route.")
            return self.render("velra_default_page")

    def render(self, template_name, **context):
        return custom_render(template_name, **context)

    def route(self, *args, **kwargs):
        return self.app.route(*args, **kwargs)

    def run(self, *args, **kwargs):
        # Key for showing errors: Ensure debug=True is passed here during development
        # Example: my_app.run(debug=True, port=5000)
        self.app.run(*args, **kwargs)