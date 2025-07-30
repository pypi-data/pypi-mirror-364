# orappgen

`orappgen` est un générateur d’applications Django structuré, conçu pour remplacer `django-admin startapp` tout en appliquant une architecture modulaire dès la création.

## 🔧 Fonctionnalités

- Création d’une app Django avec :
  - Dossier `models/`.
  - Dossier `views/`.
  - Fichier `urls.py` prêt à l’emploi
  - Fichiers standards (`admin.py`, `apps.py`, `tests.py`, et autres...)
- Génération via une simple commande CLI :
  ```bash
  startcustomapp nom_de_l_app
