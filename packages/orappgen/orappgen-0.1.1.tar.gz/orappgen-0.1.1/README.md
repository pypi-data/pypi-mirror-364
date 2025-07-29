# orappgen

**orappgen** est un générateur d'applications Django structuré. Il remplace `django-admin startapp` en créant une app avec :

- des dossiers `models/` et `views/`
- un `urls.py` prêt à l’emploi
- des fichiers comme `apps.py`, `admin.py`, `tests.py`, etc.
- des modèles et vues organisés en modules (`user.py`, `dashboard.py`, etc.)

## Installation

```bash
pip install orappgen 
```

## Utilisation
```bash
startcustomapp <nom_de_l_app>"
