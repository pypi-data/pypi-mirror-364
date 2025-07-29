import os
import sys
import re

def normalize_app_name(raw_name):
    """Convertit une chaîne brute en snake_case valide"""
    temp = re.sub(r'[^a-zA-Z0-9]+', ' ', raw_name)  # remplace tirets, points, etc.
    return '_'.join(word.lower() for word in temp.strip().split())

def app_name_to_class_name(app_name):
    """Transforme un nom snake_case en CamelCase pour une classe Config"""
    return ''.join(word.capitalize() for word in app_name.split('_')) + 'Config'

def create_app(raw_name):
    app_name = normalize_app_name(raw_name)
    class_name = app_name_to_class_name(app_name)

    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)

    # Fichiers de base
    with open(f"{app_name}/migrations/__init__.py", "w"): pass
    with open(f"{app_name}/__init__.py", "w"): pass

    with open(f"{app_name}/models/__init__.py", "w") as f:
        f.write("# models here\n")

    with open(f"{app_name}/views/__init__.py", "w") as f:
        f.write("# views here\n")

    with open(f"{app_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    with open(f"{app_name}/admin.py", "w") as f:
        f.write("from django.contrib import admin\n\n# Register your models here.\n")

    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {class_name}(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    with open(f"{app_name}/tests.py", "w") as f:
        f.write(
            "from django.test import TestCase\n\n"
            "# Create your tests here.\n"
        )

    print(f" App Django '{app_name}' créée avec succès ! (classe : {class_name})")

def main():
    if len(sys.argv) < 2:
        print("Usage : create-app <nom_app>")
    else:
        create_app(sys.argv[1])
