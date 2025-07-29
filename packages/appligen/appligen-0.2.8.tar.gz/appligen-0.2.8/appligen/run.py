import os

def create_django_app(app_name):
    os.makedirs(app_name, exist_ok=True)
    print(f"📁 Création du dossier ./{app_name}")

    # Dossier migrations/ avec __init__.py
    migrations_path = os.path.join(app_name, "migrations")
    os.makedirs(migrations_path, exist_ok=True)
    with open(os.path.join(migrations_path, "__init__.py"), "w") as f:
        f.write("")
    print("📁 Création du dossier migrations/ avec __init__.py")

    # __init__.py (vide)
    open(os.path.join(app_name, "__init__.py"), "w").close()
    print("📄 Création du fichier __init__.py")

    # apps.py
    apps_content = f"""from django.apps import AppConfig

class {app_name.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
"""
    with open(os.path.join(app_name, "apps.py"), "w") as f:
        f.write(apps_content)
    print("📄 Création du fichier apps.py")

    # models.py
    models_content = """from django.db import models

class Exemple(models.Model):
    nom = models.CharField(max_length=100)

    def __str__(self):
        return self.nom
"""
    with open(os.path.join(app_name, "models.py"), "w") as f:
        f.write(models_content)
    print("📄 Création du fichier models.py")

    # admin.py
    admin_content = """from django.contrib import admin
from .models import Exemple

admin.site.register(Exemple)
"""
    with open(os.path.join(app_name, "admin.py"), "w") as f:
        f.write(admin_content)
    print("📄 Création du fichier admin.py")

    # views.py
    views_content = f"""from django.http import HttpResponse

def home(request):
    return HttpResponse("Bienvenue dans l'app {app_name} !")
"""
    with open(os.path.join(app_name, "views.py"), "w") as f:
        f.write(views_content)
    print("📄 Création du fichier views.py")

    # tests.py
    with open(os.path.join(app_name, "tests.py"), "w") as f:
        f.write("# Tests pour l'application\n")
    print("📄 Création du fichier tests.py")

    # urls.py
    urls_content = f"""from django.urls import path
from .views import home

urlpatterns = [
    path('', home, name='{app_name}_home'),
]
"""
    with open(os.path.join(app_name, "urls.py"), "w") as f:
        f.write(urls_content)
    print("📄 Création du fichier urls.py")

    print(f"\n✅ Application Django '{app_name}' générée avec succès !")

if __name__ == "__main__":
    app_name = input("Quel nom pour votre application Django ? ").strip()
    if app_name:
        create_django_app(app_name)
    else:
        print("⛔ Aucun nom d'application fourni.")
