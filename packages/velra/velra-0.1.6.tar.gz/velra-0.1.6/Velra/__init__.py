from flask import Flask
from .core import custom_render
from .loader import CustomHtmlLoader  # import the class, not a function

class VelraApp:
    def __init__(self, import_name):
        self.app = Flask(import_name)
        
        # Use your custom HTML loader for templates
        self.app.jinja_loader = CustomHtmlLoader()
        
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return "Welcome to Velra-powered Flask app!"

    def render(self, template_name, **context):
        # Use your custom render function here
        return custom_render(template_name, **context)

    def route(self, *args, **kwargs):
        return self.app.route(*args, **kwargs)

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)
