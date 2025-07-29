Django App Generator
Un outil en ligne de commande pour créer une structure d'application Django similaire à celle générée par django-admin startapp.
Installation
pip install django-app-generator

Utilisation
Pour créer une nouvelle application Django, exécutez :
django-create-app nom_application

Pour spécifier un répertoire cible :
django-create-app nom_application --target-dir chemin/vers/repertoire

Structure générée
L'outil crée les fichiers suivants :

__init__.py
admin.py
apps.py
models.py
tests.py
urls.py
views.py
migrations/__init__.py

Prérequis

Python 3.6 ou supérieur

Licence
MIT