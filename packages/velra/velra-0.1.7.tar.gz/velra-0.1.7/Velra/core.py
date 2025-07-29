# your_test_app/velra_library/core.py
from flask import render_template, request

def custom_render(template_name, **context):
    # Log, inject variables, etc.
    context["app_name"] = "Velra"
    print(f"DEBUG: Custom rendering '{template_name}' with context: {context}")
    return render_template(template_name, **context)