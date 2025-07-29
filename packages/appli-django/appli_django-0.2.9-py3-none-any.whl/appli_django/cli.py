import os
import sys

# Convertit un nom avec underscore en CamelCase
def to_camel_case(name):
    return ''.join(word.capitalize() for word in name.split('_'))

# Fonction principale pour créer l'app
def custom_app(app_name):
    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)

    # Création du dossier templates/nom_app/
    templates_path = f"{app_name}/templates/{app_name}"
    os.makedirs(templates_path, exist_ok=True)
    with open(f"{templates_path}/index.html", "w") as f:
        f.write(f"<h1>Bienvenue dans l'application {app_name}</h1>")

    # Création du dossier static/nom_app/ avec sous-dossiers css, js
    static_path = f"{app_name}/static/{app_name}"
    os.makedirs(f"{static_path}/css", exist_ok=True)
    os.makedirs(f"{static_path}/js", exist_ok=True)

    # Exemple : fichier style.css vide
    with open(f"{static_path}/css/style.css", "w") as f:
        f.write("/* Styles CSS de l'application */\n")

    # Fichiers de base
    with open(f"{app_name}/__init__.py", "w"): pass

    with open(f"{app_name}/models/__init__.py", "w") as f:
        f.write("# models here\n")

    with open(f"{app_name}/migrations/__init__.py", "w") as f:
        f.write("# migrations here\n")

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

    class_name = to_camel_case(app_name) + "Config"
    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {class_name}(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    with open(f"{app_name}/tests.py", "w") as f:
        f.write("from django.test import TestCase\n\n# Create your tests here.\n")

    print(f"✅ App Django '{app_name}' créée avec succès, avec templates/ et static/.")

# Script principal
def main():
    if len(sys.argv) < 2:
        print(" Usage : python pack_app.py <nom_app>")
        sys.exit(1)

    raw_name = sys.argv[1]
    app_name = raw_name.strip().replace(" ", "_")

    if os.path.exists(app_name):
        print(f" Le dossier '{app_name}' existe déjà.")
        sys.exit(1)

    custom_app(app_name)

if __name__ == "__main__":
    main()
