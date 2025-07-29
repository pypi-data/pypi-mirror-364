# appli_django/cli.py
import sys
import os
from .main import custom_app

def main():
    if len(sys.argv) < 2:
        print("Usage : appli-django <nom_app>")
        sys.exit(1)

    app_name = sys.argv[1]

    if os.path.exists(app_name):
        print(f"❌ Le dossier '{app_name}' existe déjà.")
        sys.exit(1)

    custom_app(app_name)
