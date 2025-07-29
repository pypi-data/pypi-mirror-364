import os
import sys
import subprocess
import argparse

def generate_formulaire_app(app_name, target_dir='.'):
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

def main():
    parser = argparse.ArgumentParser(description="Outil CLI pour formulaire_app")
    subparsers = parser.add_subparsers(dest='command', required=True, help='Sous-commandes disponibles')

    # Sous-commande generate_app
    parser_generate_app = subparsers.add_parser('generate_formulaire_app', help='Génère une application Django')
    parser_generate_app.add_argument('app_name', help="Nom de l'application Django à créer")
    parser_generate_app.add_argument('--target', default='.', help="Dossier où créer l'application (par défaut: répertoire courant)")

    args = parser.parse_args()

    if args.command == 'generate_app':
        generate_formulaire_app(args.app_name, args.target)

if __name__ == "__main__":
    main()
