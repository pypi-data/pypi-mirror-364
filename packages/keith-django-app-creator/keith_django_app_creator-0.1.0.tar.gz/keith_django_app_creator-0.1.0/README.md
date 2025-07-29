# django-app-creator

`django-app-creator` est un outil en ligne de commande qui permet de générer rapidement la structure d'une application Django avec une organisation de fichiers personnalisée.

##  Fonctionnalités

- Crée automatiquement une application Django avec la structure suivante :
  - Un dossier `models/` contenant un fichier `__init__.py`
  - Un dossier `views/` contenant un fichier `__init__.py`
  - Un dossier `migrations/` contenant un fichier `__init__.py`
  - Un fichier `urls.py` prêt à l'emploi
  - Les fichiers standards : `admin.py`, `apps.py`, `tests.py`, `__init__.py`

##  Installation

Assurez-vous d’avoir Python 3 et `pip` installés, puis exécutez :

```bash
pip install django-app-Parfaite

## Utilisation
createapp <nom_de_l_app>