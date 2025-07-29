import os
import sys

def to_camel_case(snake_str):
    """Convertit un nom d'app comme 'ma_super_app' en 'MaSuperApp'."""
    parts = snake_str.replace("-", "_").split("_")
    return ''.join(part.capitalize() for part in parts)

def create_app(app_name):
    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)

    # Fichiers de base
    with open(f"{app_name}/__init__.py", "w"): pass

    with open(f"{app_name}/models/__init__.py", "w") as f:
        f.write("# models here\n")

    with open(f"{app_name}/views/__init__.py", "w") as f:
        f.write("# views here\n")

    with open(f"{app_name}/migrations/__init__.py", "w") as f:
        pass  # Marquer le dossier comme package Python

    with open(f"{app_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    with open(f"{app_name}/admin.py", "w") as f:
        f.write("from django.contrib import admin\n\n# Register your models here.\n")

    camel_case_name = to_camel_case(app_name)

    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {camel_case_name}Config(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    with open(f"{app_name}/tests.py", "w") as f:
        f.write(
            "from django.test import TestCase\n\n"
            "# Create your tests here.\n"
        )

    print(f"App Django '{app_name}' créée avec succès !")

def main():
    if len(sys.argv) < 2:
        print("Usage : django-create-app <nom_app>")
    else:
        create_app(sys.argv[1])
