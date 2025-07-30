import os
import sys
import re

def to_camel_case(name):
    """Convertit 'ma-super app' en 'MaSuperApp'"""
    parts = re.split(r"[-_\s]+", name)
    return ''.join(part.capitalize() for part in parts)

def to_snake_case(name):
    name = name.strip().lower().replace("-", "_").replace(" ", "_")
    name = re.sub(r'__+', '_', name)  # Remplace les doubles underscores par un seul
    return name

def create_app(raw_name):
    app_name = to_snake_case(raw_name)
    camel_case_name = to_camel_case(raw_name)

    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)
    os.makedirs(f"{app_name}/templates/{app_name}", exist_ok=True)
    os.makedirs(f"{app_name}/static/{app_name}", exist_ok=True)

    # Fichiers init
    open(f"{app_name}/__init__.py", "w").close()
    open(f"{app_name}/models/__init__.py", "w").write("# models here\n")
    open(f"{app_name}/views/__init__.py", "w").write("# views here\n")
    open(f"{app_name}/migrations/__init__.py", "w").close()

    # Fichier urls.py
    with open(f"{app_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n"
            "# from .views import ...\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    # Fichier admin.py
    with open(f"{app_name}/admin.py", "w") as f:
        f.write("from django.contrib import admin\n\n# Register your models here.\n")

    # Fichier apps.py
    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {camel_case_name}Config(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    # Fichier tests.py
    with open(f"{app_name}/tests.py", "w") as f:
        f.write(
            "from django.test import TestCase\n\n"
            "# Create your tests here.\n"
        )

    # Template HTML
    with open(f"{app_name}/templates/{app_name}/index.html", "w") as f:
        f.write(
            "<!DOCTYPE html>\n<html>\n<head>\n"
            "    <title>My Template</title>\n"
            "</head>\n<body>\n"
            "    <h1>Hello Bienvenu :-)</h1>\n"
            "</body>\n</html>\n"
        )

    # Fichier CSS
    with open(f"{app_name}/static/{app_name}/style.css", "w") as f:
        f.write("/* Style de l'application */\nbody {\n    font-family: sans-serif;\n}\n")

    print(f"Application Django '{app_name}' créée avec succès !")

def main():
    if len(sys.argv) < 2:
        print("Usage : django-create-app <nom_app>")
    else:
        raw_name = ' '.join(sys.argv[1:])  # Supporte les noms avec espaces
        create_app(raw_name)

if __name__ == "__main__":
    main()