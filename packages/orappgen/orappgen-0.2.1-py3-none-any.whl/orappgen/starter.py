import os
import sys
import re

def is_valid_django_app_name(name):
    return re.match(r"^[a-zA-Z_][a-zA-Z0-9_]*$", name)

def app_name_to_class_name(app_name):
    return ''.join(word.capitalize() for word in app_name.split('_'))

def start_custom_app(app_name, target_path="."):
    # Création du chemin complet vers l'app
    full_path = os.path.join(target_path, app_name)
    os.makedirs(full_path, exist_ok=True)

    # Création des sous-dossiers
    folders = [
        f"{full_path}/migrations",
        f"{full_path}/models",
        f"{full_path}/views",
        f"{full_path}/templates/{app_name}",
        f"{full_path}/static/{app_name}"
    ]
    for folder in folders:
        os.makedirs(folder, exist_ok=True)

    # Création des fichiers avec contenu initial
    class_name = app_name_to_class_name(app_name)
    files = {
        f"{full_path}/__init__.py": "",
        f"{full_path}/migrations/__init__.py": "",
        f"{full_path}/models/__init__.py": "# regroupement des modèles",
        f"{full_path}/views/__init__.py": "# regroupement des vues",
        f"{full_path}/templates/{app_name}/my_template.html": "<h1>Hello depuis my_template.html</h1>",
        f"{full_path}/static/{app_name}/style.css": "body { font-family: sans-serif; }",
        f"{full_path}/urls.py": f"from django.urls import path\nfrom .views.home import HomeView\n\nurlpatterns = [\n    path('', HomeView.as_view(), name='{app_name}_home'),\n]",
        f"{full_path}/apps.py": f"from django.apps import AppConfig\n\nclass {class_name}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'",
        f"{full_path}/admin.py": "# admin Formulaire",
        f"{full_path}/tests.py": "# tests",
    }

    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content)

    print(f"Application Django '{app_name}' créée dans '{full_path}/'.")

def main():
    if len(sys.argv) == 2:
        app_name = sys.argv[1]
        target_path = "."
    elif len(sys.argv) == 3:
        app_name = sys.argv[1]
        target_path = sys.argv[2]
    else:
        print("Usage : startcustomapp <nom_de_l_app> [chemin_cible]")
        sys.exit(1)

    if not is_valid_django_app_name(app_name):
        print(f"Nom invalide : '{app_name}'")
        print("Le nom doit commencer par une lettre, et contenir uniquement lettres, chiffres ou underscores.")
        sys.exit(1)

    start_custom_app(app_name, target_path)
