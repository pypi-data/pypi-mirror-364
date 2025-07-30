import os
from django.core.management.base import BaseCommand, CommandError

class Command(BaseCommand):
    help = "Crée une nouvelle application Django avec des fichiers préconfigurés."

    def add_arguments(self, parser):
        parser.add_argument("app_name", type=str)

    def handle(self, *args, **options):
        app_name = options["app_name"]
        try:
            os.makedirs(app_name)
            with open(os.path.join(app_name, "models.py"), "w") as f:
                f.write("from django.db import models\n\nclass ExampleModel(models.Model):\n    name = models.CharField(max_length=100)\n")
            with open(os.path.join(app_name, "views.py"), "w") as f:
                f.write("from django.shortcuts import render\n\ndef index(request):\n    return render(request, f'{app_name}/index.html')\n")
            with open(os.path.join(app_name, "urls.py"), "w") as f:
                f.write("from django.urls import path\nfrom . import views\n\nurlpatterns = [\n    path('', views.index, name='index'),\n]\n")
            with open(os.path.join(app_name, "forms.py"), "w") as f:
                f.write("from django import forms\n\nclass ExampleForm(forms.Form):\n    name = forms.CharField(max_length=100)\n")
            with open(os.path.join(app_name, "admin.py"), "w") as f:
                f.write("from django.contrib import admin\nfrom .models import ExampleModel\n\nadmin.site.register(ExampleModel)\n")
            with open(os.path.join(app_name, "apps.py"), "w") as f:
                f.write(f"from django.apps import AppConfig\n\nclass {{app_name.capitalize()}}Config(AppConfig):\n    name = '{{app_name}}'\n".replace("{{app_name}}", app_name).replace("{{app_name.capitalize()}}", app_name.capitalize()))
            os.makedirs(os.path.join(app_name, "templates", app_name))
            with open(os.path.join(app_name, "templates", app_name, "index.html"), "w") as f:
                f.write(f"<h1>Bienvenue dans l'application {{app_name}} !</h1>".replace("{{app_name}}", app_name))
            self.stdout.write(self.style.SUCCESS(f"L'application {{app_name}} a été créée avec succès.".replace("{{app_name}}", app_name)))
        except Exception as e:
            raise CommandError(f"Erreur lors de la création : {{e}}")
