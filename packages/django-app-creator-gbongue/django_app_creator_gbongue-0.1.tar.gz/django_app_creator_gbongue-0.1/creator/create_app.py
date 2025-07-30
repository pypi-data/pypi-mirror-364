import os
import sys

def run():
    if len(sys.argv) != 2:
        print("Usage: python -m creator <app_name>")
        return

    app_name = sys.argv[1]
    if os.path.exists(app_name):
        print(f"L'app '{app_name}' existe déjà.")
        return

    os.makedirs(os.path.join(app_name, 'migrations'))
    os.makedirs(os.path.join(app_name, 'templates', app_name))
    os.makedirs(os.path.join(app_name, 'static', app_name))

    with open(os.path.join(app_name, '__init__.py'), 'w') as f:
        pass

    files = {
        'admin.py': "from django.contrib import admin\n",
        'apps.py': f"from django.apps import AppConfig\n\nclass {app_name.capitalize()}Config(AppConfig):\n    name = '{app_name}'\n",
        'models.py': "from django.db import models\n",
        'tests.py': "from django.test import TestCase\n",
        'views.py': "from django.shortcuts import render\n",
    }

    for filename, content in files.items():
        with open(os.path.join(app_name, filename), 'w') as f:
            f.write(content)

    print(f"L'application Django '{app_name}' a été créée avec succès.")
