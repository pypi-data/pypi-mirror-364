import os
import sys

def to_pascal_case(name: str) -> str:
    """Transforme 'blog_app' en 'BlogApp'"""
    return ''.join(word.capitalize() for word in name.split('_'))

def normalize_app_name(name: str) -> str:
    """Remplace les espaces et tirets par des underscores"""
    return name.strip().replace(" ", "_").replace("-", "_")

def create_app(app_name: str):
    app_name = normalize_app_name(app_name)

    os.makedirs(app_name, exist_ok=True)

    # Dossiers principaux
    os.makedirs(os.path.join(app_name, "models"), exist_ok=True)
    os.makedirs(os.path.join(app_name, "views"), exist_ok=True)
    os.makedirs(os.path.join(app_name, "migrations"), exist_ok=True)
    os.makedirs(os.path.join(app_name, "templates", app_name), exist_ok=True)
    os.makedirs(os.path.join(app_name, "static", app_name), exist_ok=True)

    # Fichiers __init__.py
    open(os.path.join(app_name, "__init__.py"), "w").close()
    with open(os.path.join(app_name, "models", "__init__.py"), "w") as f:
        f.write("# models here\n")
    with open(os.path.join(app_name, "views", "__init__.py"), "w") as f:
        f.write("# views here\n")
    open(os.path.join(app_name, "migrations", "__init__.py"), "w").close()

    # urls.py
    with open(os.path.join(app_name, "urls.py"), "w") as f:
        f.write(
            "from django.urls import path\n"
            "from . import views\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    # admin.py
    with open(os.path.join(app_name, "admin.py"), "w") as f:
        f.write("from django.contrib import admin\n\n# Register your models here.\n")

    # apps.py
    class_name = to_pascal_case(app_name) + "Config"
    with open(os.path.join(app_name, "apps.py"), "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {class_name}(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    # tests.py
    with open(os.path.join(app_name, "tests.py"), "w") as f:
        f.write("from django.test import TestCase\n\n# Create your tests here.\n")

    print(f"✅ Application Django '{app_name}' créée avec succès !")

def main():
    if len(sys.argv) < 2:
        print("❌ Usage : python -m appligen.generator <nom_de_l_app>")
        sys.exit(1)

    raw_name = sys.argv[1]
    create_app(raw_name)

if __name__ == "__main__":
    main()
