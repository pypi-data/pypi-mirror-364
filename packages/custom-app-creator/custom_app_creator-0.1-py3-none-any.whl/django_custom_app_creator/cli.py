import argparse
import os
import re


def slugify(name):
    # remplace tirets et espaces par underscore et minuscule
    return re.sub(r'[-\\s]+', '_', name.strip().lower())

def class_name(name):
    # Convertit un nom en CamelCase
    return ''.join(word.capitalize() for word in re.split(r'[-_\\s]+', name.strip()))

def create_app(app_name):
    module_name = slugify(app_name)
    class_name_config = class_name(app_name) + "Config"
    verbose_name = " ".join(word.capitalize() for word in re.split(r'[-_\\s]+', app_name.strip()))

    try:
        os.makedirs(f"{module_name}/templates/{module_name}", exist_ok=True)
        
        with open(os.path.join(module_name, "models.py"), "w") as f:
            f.write("from django.db import models\n\nclass ExampleModel(models.Model):\n    name = models.CharField(max_length=100)\n")

        with open(os.path.join(module_name, "views.py"), "w") as f:
            f.write(f"from django.shortcuts import render\n\ndef index(request):\n    return render(request, '{module_name}/index.html')\n")

        with open(os.path.join(module_name, "urls.py"), "w") as f:
            f.write("from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('', views.index, name='index'),\n]\n")

        with open(os.path.join(module_name, "admin.py"), "w") as f:
            f.write("from django.contrib import admin\nfrom .models import ExampleModel\n\nadmin.site.register(ExampleModel)\n")

        with open(os.path.join(module_name, "apps.py"), "w") as f:
            f.write(f"from django.apps import AppConfig\n\nclass {class_name_config}(AppConfig):\n    default_auto_field = 'django.db.models.BigAutoField'\n    name = '{module_name}'\n    verbose_name = '{verbose_name}'\n")

        with open(os.path.join(module_name, "__init__.py"), "w") as f:
            f.write("")

        with open(os.path.join(module_name, "templates", module_name, "index.html"), "w") as f:
            f.write(f"<h1>Bienvenue dans l'application {verbose_name} !</h1>")

        os.makedirs(f"{module_name}/static/{module_name}", exist_ok=True)

        with open(os.path.join(module_name, "static", module_name, "style.css"), "w") as f:
            f.write("body { font-family: sans-serif; }")

            
        print(f"Ajoutez '{module_name}' dans INSTALLED_APPS de settings.py.")
    except Exception as e:
        print(f"[✖] Erreur : {e}")

def main():
    parser = argparse.ArgumentParser(description="Créateur d'application Django")
    parser.add_argument('name', nargs='+', help="Nom de l'application (mots autorisés sans guillemets)")
    args = parser.parse_args()
    app_name = '_'.join(args.name)  # fusionne la liste en chaîne
    create_app(app_name)
