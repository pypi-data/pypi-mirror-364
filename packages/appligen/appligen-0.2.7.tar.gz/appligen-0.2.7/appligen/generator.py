import os
import sys

def to_pascal_case(name: str) -> str:
    """Transforme un nom comme 'blog_app' en 'BlogApp'"""
    return ''.join(word.capitalize() for word in name.split('_'))

def create_django_app(app_name: str, target_dir: str = ".") -> None:
    """Crée la structure de base d'une application Django avec models/ et views/ en dossiers"""
    app_path = os.path.join(target_dir, app_name)
    if os.path.exists(app_path):
        print(f"⚠️ L'app '{app_name}' existe déjà dans {target_dir}")
        return

    os.makedirs(app_path)
    print(f"📁 Création du dossier : {app_path}")

    # Dossier migrations
    migrations_path = os.path.join(app_path, "migrations")
    os.makedirs(migrations_path)
    with open(os.path.join(migrations_path, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    print(f"📁 Création du dossier : {migrations_path}/__init__.py")

    # Dossier models avec __init__.py vide
    models_path = os.path.join(app_path, "models")
    os.makedirs(models_path)
    with open(os.path.join(models_path, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    print(f"📁 Création du dossier : {models_path}/__init__.py")

    # Dossier views avec __init__.py vide
    views_path = os.path.join(app_path, "views")
    os.makedirs(views_path)
    with open(os.path.join(views_path, "__init__.py"), "w", encoding="utf-8") as f:
        f.write("")
    print(f"📁 Création du dossier : {views_path}/__init__.py")

    # Fichiers à la racine
    files_content = {
        "__init__.py": "",
        "admin.py": "from django.contrib import admin\n\n# Register your models here.\n",
        "apps.py": (
            "from django.apps import AppConfig\n\n\n"
            f"class {to_pascal_case(app_name)}Config(AppConfig):\n"
            "    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        ),
        "urls.py": "from django.urls import path\n\nurlpatterns = [\n    # path('', views.home, name='home'),\n]\n",
        "tests.py": "from django.test import TestCase\n\n# Create your tests here.\n",
    }

    for filename, content in files_content.items():
        with open(os.path.join(app_path, filename), "w", encoding="utf-8") as f:
            f.write(content)
        print(f"📄 Création du fichier : {filename}")

    print(f"\n✅ Application Django '{app_name}' créée avec succès.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("❌ Usage : python -m appligen.generator <nom_de_l_app>")
        sys.exit(1)

    app_name = sys.argv[1]
    create_django_app(app_name)
