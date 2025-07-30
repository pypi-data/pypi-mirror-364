import os
import sys

def create_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, 'w') as f:
        f.write(content)

def create_custom_app(app_name):
    if os.path.exists(app_name):
        print(f"❌ Le dossier '{app_name}' existe déjà.")
        return

    # Contenu par défaut pour certains fichiers
    init_py = "# __init__.py\n"
    urls_py = f"""# urls.py
from django.urls import path

urlpatterns = [
    # path('', views.home, name='{app_name}_home'),
]
"""
    apps_py = f"""# apps.py
from django.apps import AppConfig

class {app_name.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
"""
    admin_py = "# admin.py\n"
    tests_py = "# tests.py\n"
    html_template = f"<!-- templates/{app_name}/my_template.html -->\n<h1>Template de {app_name}</h1>"
    css_content = "/* style.css */\nbody { background-color: #f0f0f0; }"

    files = {
        f"{app_name}/migrations/__init__.py": init_py,
        f"{app_name}/models/__init__.py": init_py,
        f"{app_name}/views/__init__.py": init_py,
        f"{app_name}/templates/{app_name}/my_template.html": html_template,
        f"{app_name}/static/{app_name}/style.css": css_content,
        f"{app_name}/__init__.py": init_py,
        f"{app_name}/urls.py": urls_py,
        f"{app_name}/apps.py": apps_py,
        f"{app_name}/admin.py": admin_py,
        f"{app_name}/tests.py": tests_py,
    }

    for path, content in files.items():
        create_file(path, content)

    print(f"✅ Application Django personnalisée '{app_name}' générée avec succès.")

def main():
    if len(sys.argv) != 2:
        print("Utilisation : django-appgen <nom_app>")
        sys.exit(1)

    app_name = sys.argv[1]
    create_custom_app(app_name)
