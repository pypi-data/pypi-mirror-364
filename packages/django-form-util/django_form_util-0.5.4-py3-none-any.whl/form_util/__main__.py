import sys
from pathlib import Path
import re
import os
import importlib.resources as pkg_resources


def to_camel_case(name):
    """Convertit 'ma-super app' en 'MaSuperApp'"""
    parts = re.split(r"[-_\s]+", name)
    return ''.join(part.capitalize() for part in parts)

def to_snake_case(name):
    """Convertit 'MaSuper App' ou 'maSuper-App' en 'ma_super_app'"""
    name = name.strip().lower().replace("-", "_").replace(" ", "_")
    name = re.sub(r'__+', '_', name)  # Enlève doublons de '_'
    return name

def create_app(raw_name):
    app_name = to_snake_case(raw_name)
    camel_case_name = to_camel_case(raw_name)

    os.makedirs(app_name, exist_ok=True)
    os.makedirs(f"{app_name}/models", exist_ok=True)
    os.makedirs(f"{app_name}/views", exist_ok=True)
    os.makedirs(f"{app_name}/migrations", exist_ok=True)
    os.makedirs(f"{app_name}/templates/{app_name}", exist_ok=True)
    os.makedirs(f"{app_name}/static/{app_name}", exist_ok=True)

    # Fichiers init
    open(f"{app_name}/__init__.py", "w").close()
    open(f"{app_name}/models/__init__.py", "w").write("# models here\n")
    open(f"{app_name}/migrations/__init__.py", "w").close()

    # Fichier urls.py
    with open(f"{app_name}/urls.py", "w") as f:
        f.write(
            "from django.urls import path\n"
            "# from .views import ...\n\n"
            "urlpatterns = [\n"
            f"    path('', views.index, name='{app_name}'),\n"
            "]\n"
        )


    # Fichier apps.py
    with open(f"{app_name}/apps.py", "w") as f:
        f.write(
            "from django.apps import AppConfig\n\n"
            f"class {camel_case_name}Config(AppConfig):\n"
            f"    default_auto_field = 'django.db.models.BigAutoField'\n"
            f"    name = '{app_name}'\n"
        )


    # Fichier views.py
    with open(f"{app_name}/views.py", "w") as f:
        f.write(
            "from django.shortcuts import render\n"
            f"from .forms import WelcomeForm\n\n\n"
            "def welcome_view(request):\n"
            f"    return render(request, '{app_name}/index.html', {{\n"
            "        'form': WelcomeForm(),\n"
            "        'user': request.user\n"
            "    })\n"
        )

    # Fichier forms.py
    with open(f"{app_name}/forms.py", "w") as f:
        f.write(
            "from django import forms\n\n"
            "class WelcomeForm(forms.Form):\n"
            "    name = forms.CharField(label='Nom', max_length=100)\n"
            "    email = forms.EmailField(label='Email')\n"
            "    message = forms.CharField(label='Message', widget=forms.Textarea)\n"
        )


    # Chemins des fichiers modèles
    base_dir = Path(__file__).resolve().parent
    template_file = base_dir / "templates" / "form_util" / "index.html"
    style_file = base_dir / "static" / "form_util" / "style.css"

    # Copier HTML
    with pkg_resources.files("form_util.templates.form_util").joinpath("index.html").open("rb") as src:
        target_html = Path(f"{app_name}/templates/{app_name}/index.html")
        with open(target_html, "wb") as dst:
            dst.write(src.read())

    # Copier CSS
    with pkg_resources.files("form_util.static.form_util").joinpath("style.css").open("rb") as src:
        target_css = Path(f"{app_name}/static/{app_name}/style.css")
        with open(target_css, "wb") as dst:
            dst.write(src.read())

    print(f"Application Django '{app_name}' créée avec succès !")


def main():
    if len(sys.argv) < 2:
        print("❗ Nom de l'application requis.")
        print("Exemple : form_util <nom_app>")
    else:
        raw_name = ' '.join(sys.argv[1:])  # Supporte les noms avec espaces
        create_app(raw_name)
        return
