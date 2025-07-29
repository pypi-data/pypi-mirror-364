# formulaire_app

Un outil CLI pour générer des applications Django réutilisables dans n’importe quel projet.


Quick start

    Add “formulaire_app” to your INSTALLED_APPS setting like this:

    INSTALLED_APPS = [
        ...,
        "formulaire_app",
    ]

    Include the app URLconf in your project urls.py like this:

    path("formulaire_app/", include("formulaire_app.urls")),



## Installation

```bash
pip install formulaire_app

## Utulisation


generate_formulaire_app nom_de_lapp 

python manage.py migrate 

python manage.py runserver

