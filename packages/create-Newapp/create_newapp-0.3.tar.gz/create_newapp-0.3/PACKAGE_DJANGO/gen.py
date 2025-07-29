import os
import shutil

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), "..", "templates_app")

def create_django_app(app_name, base_path="."):
    target_path = os.path.join(base_path, app_name)
    os.makedirs(target_path, exist_ok=True)

    for filename in ["models.py", "views.py", "urls.py", "admin.py", "forms.py"]:
        shutil.copy(os.path.join(TEMPLATES_DIR, filename), os.path.join(target_path, filename))

    # Crée __init__.py
    open(os.path.join(target_path, "__init__.py"), "w").close()

    # Copie le dossier de templates
    shutil.copytree(os.path.join(TEMPLATES_DIR, "templates"), os.path.join(target_path, "templates"))

    print(f"Application Django '{app_name}' créée avec succès.")
