# velra/__init__.py

from flask import Flask

class VelraApp:
    def __init__(self, import_name):
        self.app = Flask(import_name)
        self._setup_routes()

    def _setup_routes(self):
        @self.app.route('/')
        def home():
            return "Welcome to Velra-powered Flask app!"

    def run(self, *args, **kwargs):
        self.app.run(*args, **kwargs)
