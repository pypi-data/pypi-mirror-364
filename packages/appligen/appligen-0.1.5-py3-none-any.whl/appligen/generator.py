import os

def create_django_app(app_name: str, target_dir: str = ".") -> None:

    app_path = os.path.join(target_dir, app_name)
    if os.path.exists(app_path):
        print(f"L'app '{app_name}' existe déjà dans {target_dir}")
        return

    os.makedirs(app_path)
    print(f"Création du dossier {app_path}")

    # Création du dossier migrations
    migrations_path = os.path.join(app_path, "migrations")
    os.makedirs(migrations_path)
    print(f"Création du dossier migrations")

    # Fichiers à créer avec contenu minimal
    files_content = {
        "__init__.py": "",
        "admin.py": "from django.contrib import admin\n\n# Register your models here.\n",
        "apps.py": f"from django.apps import AppConfig\n\n\nclass {app_name.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'\n",
        "models.py": "from django.db import models\n\n# Create your models here.\n",
        "tests.py": "from django.test import TestCase\n\n# Create your tests here.\n",
        "views.py": "from django.shortcuts import render\n\n# Create your views here.\n",
    }

    # Fichier pour le dossier migrations
    migrations_files = {
        "__init__.py": "",
    }

    # Création des fichiers principaux
    for filename, content in files_content.items():
        with open(os.path.join(app_path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Création du fichier {filename}")

    # Création des fichiers dans migrations
    for filename, content in migrations_files.items():
        with open(os.path.join(migrations_path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Création du fichier migrations/{filename}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("appligen <nom_de_l_app>")
        sys.exit(1)
    app_name = sys.argv[1]
    create_django_app(app_name)