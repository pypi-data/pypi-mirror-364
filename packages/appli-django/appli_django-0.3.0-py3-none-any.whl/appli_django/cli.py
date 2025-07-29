import os
import sys
import re

# ➤ Nom du dossier et du champ 'name' : snake_case (underscore)
def to_snake_case(name):
    return re.sub(r'[-\s]+', '_', name.strip().lower())

# ➤ Nom de la classe : CamelCase
def to_camel_case(name):
    return ''.join(word.capitalize() for word in re.split(r'[-\s_]+', name.strip()))

def custom_app(raw_name):
    app_name = to_snake_case(raw_name)
    class_name = to_camel_case(raw_name) + "Config"

    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)

    # Templates
    templates_path = f"{app_name}/templates/{app_name}"
    os.makedirs(templates_path, exist_ok=True)
    with open(f"{templates_path}/index.html", "w") as f:
        f.write(f"<h1>Bienvenue dans l'application {app_name}</h1>")

    # Static
    static_path = f"{app_name}/static/{app_name}"
    os.makedirs(f"{static_path}/css", exist_ok=True)
    os.makedirs(f"{static_path}/js", exist_ok=True)
    os.makedirs(f"{static_path}/images", exist_ok=True)
    with open(f"{static_path}/css/style.css", "w") as f:
        f.write("/* CSS de base */")

    # Fichiers initiaux
    open(f"{app_name}/__init__.py", "w").close()
    open(f"{app_name}/models/__init__.py", "w").close()
    open(f"{app_name}/views/__init__.py", "w").close()
    open(f"{app_name}/migrations/__init__.py", "w").close()

    with open(f"{app_name}/admin.py", "w") as f:
        f.write("from django.contrib import admin\n")

    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {class_name}(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )

    with open(f"{app_name}/tests.py", "w") as f:
        f.write("from django.test import TestCase\n\n")

    with open(f"{app_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n\n"
            "urlpatterns = [\n"
            "    # path('', views.index, name='index'),\n"
            "]\n"
        )

    print(f" App Django '{app_name}' (classe: {class_name}) créée avec succès.")

def main():
    if len(sys.argv) < 2:
        print(" Usage : python pack_app.py <nom_app>")
        sys.exit(1)

    raw_name = " ".join(sys.argv[1:])
    custom_app(raw_name)

if __name__ == "__main__":
    main()
