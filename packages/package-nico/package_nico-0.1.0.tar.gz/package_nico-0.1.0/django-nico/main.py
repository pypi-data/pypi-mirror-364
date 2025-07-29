import os

def create_file(path, content=""):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)

def generate_django_app(app_name):
    base_path = os.path.join(os.getcwd(), app_name)
    os.makedirs(os.path.join(base_path, "migrations"), exist_ok=True)
    os.makedirs(os.path.join(base_path, "templates", app_name), exist_ok=True)

    files = {
        os.path.join(base_path, "__init__.py"): "",
        os.path.join(base_path, "admin.py"): "from django.contrib import admin\nfrom .models import *\n\n",
        os.path.join(base_path, "apps.py"): f"from django.apps import AppConfig\n\nclass {app_name.capitalize()}Config(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{app_name}'\n",
        os.path.join(base_path, "forms.py"): "from django import forms\n\n",
        os.path.join(base_path, "models.py"): "from django.db import models\n\n",
        os.path.join(base_path, "tests.py"): "from django.test import TestCase\n\n",
        os.path.join(base_path, "urls.py"): f"from django.urls import path\nfrom . import views\n\napp_name = '{app_name}'\n\nurlpatterns = [\n    path('', views.index, name='index'),\n]\n",
        os.path.join(base_path, "views.py"): f"from django.shortcuts import render\n\ndef index(request):\n    return render(request, '{app_name}/base.html')\n",
        os.path.join(base_path, "migrations", "__init__.py"): "",
        os.path.join(base_path, "templates", app_name, "base.html"): f"<!DOCTYPE html>\n<html>\n<head>\n    <title>{app_name.capitalize()} - Accueil</title>\n</head>\n<body>\n    <h1>Bienvenue dans l'application {app_name.capitalize()}</h1>\n</body>\n</html>\n",
    }

    for path, content in files.items():
        create_file(path, content)

    print(f"L'application Django '{app_name}' a été créée avec succès !")

def main():
    import sys
    if len(sys.argv) != 2:
        print("Usage: package-nico <nom_de_l_app>")
        return

    app_name = sys.argv[1]
    generate_django_app(app_name)

if __name__ == "__main__":
    main()
