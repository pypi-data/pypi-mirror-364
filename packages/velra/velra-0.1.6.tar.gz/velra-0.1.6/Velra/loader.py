from jinja2 import BaseLoader, TemplateNotFound

class CustomHtmlLoader(BaseLoader):
    def get_source(self, environment, template):
        # For testing, return simple HTML with the template name
        source = f"<h1>This would be your rendered template: {template}</h1>"
        # No filename, not up-to-date info
        return source, None, lambda: True
