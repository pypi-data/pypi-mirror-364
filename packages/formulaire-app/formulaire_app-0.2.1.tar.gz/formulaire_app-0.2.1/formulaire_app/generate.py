import os
import sys

def generate_formulaire_app(app_name, target_dir='.'):
    # Crée le répertoire cible s’il n’existe pas
    os.makedirs(target_dir, exist_ok=True)
    
    # Place-toi dans le répertoire cible
    os.chdir(target_dir)

    # Crée l'application Django avec startapp
    exit_code = os.system(f'django-admin startapp {app_name}')
    
    if exit_code != 0:
        print("Erreur : échec de la création de l'application.")
        sys.exit(1)
    
    print(f"✅ Application Django '{app_name}' générée avec succès dans {os.path.abspath(target_dir)}")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description="Génère une application Django réutilisable.")
    parser.add_argument('app_name', help="Nom de l'application Django à créer")
    parser.add_argument('--target', default='.', help="Dossier où créer l'application (défaut: répertoire courant)")

    args = parser.parse_args()
    generate_formulaire_app(args.app_name, args.target)
