import os
import sys


def to_pascal_case(name: str) -> str:
    return ''.join(word.capitalize() for word in name.split('_'))


def create_django_app(app_name: str, target_dir: str = ".") -> None:
    app_path = os.path.join(target_dir, app_name)
    if os.path.exists(app_path):
        print(f"⚠️ L'app '{app_name}' existe déjà dans {target_dir}")
        return

    # Création du dossier principal de l'app
    os.makedirs(app_path, exist_ok=True)
    print(f"📁 Création du dossier : {app_path}")

    # Création du dossier migrations avec debug
    migrations_path = os.path.join(app_path, "migrations")
    os.makedirs(migrations_path, exist_ok=True)
    print(f"📁 Création du dossier : {app_name}/migrations")

    try:
        os.makedirs(migrations_path, exist_ok=True)
        print(f"📁 Création du dossier : {migrations_path}")
        print(f"✅ Debug - Migrations créées : {os.path.exists(migrations_path)}")
    except Exception as e:
        print(f"❌ Erreur création migrations : {e}")
        return

    # Création du fichier __init__.py dans migrations
    migrations_init_file = os.path.join(migrations_path, "__init__.py")
    try:
        with open(migrations_init_file, "w", encoding="utf-8") as f:
            f.write("")
        print(f"📄 Création du fichier : {os.path.join(app_name, 'migrations', '__init__.py')}")
        print(f"✅ Debug - Init file créé : {os.path.exists(migrations_init_file)}")
    except Exception as e:
        print(f"❌ Erreur création __init__.py : {e}")

    # Contenu des fichiers principaux
    files_content = {
        "__init__.py": "",
        "admin.py": "from django.contrib import admin\n\n# Register your models here.\n",
        "apps.py": (
            "from django.apps import AppConfig\n\n\n"
            f"class {to_pascal_case(app_name)}Config(AppConfig):\n"
            "    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        ),
        "models.py": "from django.db import models\n\n# Create your models here.\n",
        "tests.py": "from django.test import TestCase\n\n# Create your tests here.\n",
        "views.py": "from django.shortcuts import render\n\n# Create your views here.\n",
        "urls.py": "from django.urls import path\n\nurlpatterns = [\n    # path('', views.home, name='home'),\n]\n",
    }

    # Création des fichiers principaux
    for filename, content in files_content.items():
        filepath = os.path.join(app_path, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Création du fichier : {os.path.join(app_name, filename)}")

    print(f"\n✅ Application Django '{app_name}' créée avec succès dans {app_path}")
    print(f"📋 Structure créée :")
    print(f"   {app_name}/")
    print(f"   ├── __init__.py")
    print(f"   ├── admin.py")
    print(f"   ├── apps.py")
    print(f"   ├── models.py")
    print(f"   ├── tests.py")
    print(f"   ├── views.py")
    print(f"   ├── urls.py")
    print(f"   └── migrations/")
    print(f"       └── __init__.py")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage : python -m appligen.generator <nom_de_l_app>")
        sys.exit(1)

    app_name = sys.argv[1]
    create_django_app(app_name)