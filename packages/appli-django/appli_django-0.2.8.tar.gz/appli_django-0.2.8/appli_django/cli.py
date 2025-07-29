import os
import sys

# Convertit un nom d'application avec des underscores en CamelCase
def to_camel_case(name):
    return ''.join(word.capitalize() for word in name.split('_'))

def custom_app(app_name):
    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)

    # Fichier __init__.py racine
    with open(f"{app_name}/__init__.py", "w"): pass

    # Dossiers avec leurs fichiers init
    with open(f"{app_name}/models/__init__.py", "w") as f:
        f.write("# models here\n")

    with open(f"{app_name}/migrations/__init__.py", "w") as f:
        f.write("# migrations here\n")

    with open(f"{app_name}/views/__init__.py", "w") as f:
        f.write("# views here\n")

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

    # apps.py avec nom CamelCase pour la classe
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
        f.write(
            "from django.test import TestCase\n\n"
            "# Create your tests here.\n"
        )

    print(f" App Django '{app_name}' créée avec succès !")

def main():
    if len(sys.argv) < 2:
        print(" Usage : python pack_app.py <nom_app>")
        sys.exit(1)
    else:
        app_name = sys.argv[1]
        if os.path.exists(app_name):
            print(f"Le dossier '{app_name}' existe déjà. Choisissez un autre nom.")
            sys.exit(1)
        custom_app(app_name)

if __name__ == "__main__":
    main()