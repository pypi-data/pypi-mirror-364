import os
import sys
import re

def to_camel_case(value):
    value = re.sub(r'[^a-zA-Z0-9]', ' ', value)
    return ''.join(word.capitalize() for word in value.split())

def create_app(app_name):
    # Création des répertoires principaux
    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)
    os.makedirs(f"{app_name}/templates/{app_name}", exist_ok=True)
    os.makedirs(f"{app_name}/static/{app_name}", exist_ok=True)

    # Fichiers __init__.py
    open(f"{app_name}/__init__.py", "w").close()
    open(f"{app_name}/migrations/__init__.py", "w").close()
    with open(f"{app_name}/models/__init__.py", "w") as f:
        f.write("# models here\n")
    with open(f"{app_name}/views/__init__.py", "w") as f:
        f.write("# views here\n")

    # Fichier HTML template vide
    with open(f"{app_name}/templates/{app_name}/my_template.html", "w") as f:
        f.write("")  # Fichier HTML vide

    # Fichier CSS vide
    with open(f"{app_name}/static/{app_name}/style.css", "w") as f:
        f.write("")  # Fichier CSS vide

    # urls.py
    with open(f"{app_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    # admin.py
    with open(f"{app_name}/admin.py", "w") as f:
        f.write("from django.contrib import admin\n\n# Register your models here.\n")

    # apps.py
    class_name = to_camel_case(app_name) + "Config"
    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {class_name}(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    # tests.py
    with open(f"{app_name}/tests.py", "w") as f:
        f.write("from django.test import TestCase\n\n# Create your tests here.\n")

    print(f"App Django '{app_name}' créée avec succès avec templates/ et static/.")

def main():
    if len(sys.argv) < 2:
        print("Usage : django-create-app <nom_app>")
    else:
        create_app(sys.argv[1])

if __name__ == "__main__":
    main()