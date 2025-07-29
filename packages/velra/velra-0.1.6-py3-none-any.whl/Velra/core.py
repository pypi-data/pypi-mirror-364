from flask import render_template, request

def custom_render(template_name, **context):
    # Log, inject variables, etc.
    context["app_name"] = "Velra"
    return render_template(template_name, **context)
