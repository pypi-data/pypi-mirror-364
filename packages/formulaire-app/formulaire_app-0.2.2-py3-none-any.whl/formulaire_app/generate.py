import os
import subprocess
import sys

def generate_app(app_name, target_dir='.'):
    os.makedirs(target_dir, exist_ok=True)
    original_dir = os.getcwd()
    try:
        os.chdir(target_dir)
        result = subprocess.run(['django-admin', 'startapp', app_name])
        if result.returncode != 0:
            print("Erreur : échec de la création de l'application.")
            sys.exit(1)
        print(f"✅ Application Django '{app_name}' générée avec succès dans {os.path.abspath(target_dir)}")
    finally:
        os.chdir(original_dir)
