# your_test_app/velra_library/loader.py
from jinja2 import BaseLoader, TemplateNotFound, FileSystemLoader
import os

class CustomHtmlLoader(BaseLoader):
    def __init__(self, template_folder):
        # Initialize a standard FileSystemLoader to handle actual files
        self.file_loader = FileSystemLoader(template_folder)

    def get_source(self, environment, template):
        try:
            # First, try to get the source from the file system
            source, filename, uptodate = self.file_loader.get_source(environment, template)
            print(f"DEBUG: Loaded '{template}' from file system: {filename}")
            return source, filename, uptodate
        except TemplateNotFound:
            # If the template file is not found, fall back to your custom generation
            print(f"DEBUG: Template '{template}' not found in file system. Using custom generation.")
            source = f"<h1>This would be your custom-generated template: {template}</h1>"
            # For custom-generated content, there's no specific filename or up-to-date check based on a file
            return source, None, lambda: True