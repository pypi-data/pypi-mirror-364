import argparse
from .generate import generate_app  # ou adapte selon ton organisation

def main():
    parser = argparse.ArgumentParser(description="Génère une application Django.")
    parser.add_argument("app_name", help="Nom de l'application Django à générer")
    parser.add_argument("--target", default=".", help="Répertoire de destination")
    
    args = parser.parse_args()
    generate_app(args.app_name, args.target)
