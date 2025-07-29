import os
import sys

def main():
    if len(sys.argv) != 2:
        print("Usage : startcustomapp <nom_de_l_app>")
        sys.exit(1)

    app_name = sys.argv[1]
    start_custom_app(app_name)
    print(f"Application Django '{app_name}' générée.")

def start_custom_app(app_name):
    # Dossiers principaux
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)

    # Fichiers standard
    files = {
        f"{app_name}/models/__init__.py": "# regroupement des modèles",
        f"{app_name}/models/base.py": "from django.db import models\n\nclass BaseModel(models.Model):\n    created_at = models.DateTimeField(auto_now_add=True)\n\n    class Meta:\n        abstract = True",
        f"{app_name}/models/user.py": "from django.db import models\n\nclass User(BaseModel):\n    name = models.CharField(max_length=100)",
        f"{app_name}/views/__init__.py": "# regroupement des vues",
        f"{app_name}/views/home.py": "from django.views.generic import TemplateView\n\nclass HomeView(TemplateView):\n    template_name = 'home.html'",
        f"{app_name}/views/dashboard.py": "from django.views.generic import TemplateView\n\nclass DashboardView(TemplateView):\n    template_name = 'dashboard.html'",
        f"{app_name}/urls.py": "from django.urls import path\nfrom .views.home import HomeView\n\nurlpatterns = [\n    path('', HomeView.as_view(), name='home'),\n]",
        f"{app_name}/apps.py": f"from django.apps import AppConfig\n\nclass {app_name.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'",
        f"{app_name}/admin.py": "# admin site config",
        f"{app_name}/tests.py": "# tests",
        f"{app_name}/migrations/__init__.py": "",
    }

    for path, content in files.items():
        with open(path, "w") as f:
            f.write(content)
