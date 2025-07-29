# create_django_app_irwin/cli.py
import os
import sys

def create_app(app_name):
    if not app_name:
        print("Veuillez fournir un nom pour l'application.")
        return
    if os.path.exists(app_name):
        print(f"❌ Le dossier '{app_name}' existe déjà.")
        return
    
    print(f"🚀 Création de l'application Django '{app_name}'...\n")
    os.makedirs(app_name)
    os.makedirs(os.path.join(app_name, 'migrations'))
    
    # 1. __init__.py
    write_file(app_name, '__init__.py', '')
    
    # 2. admin.py
    write_file(app_name, 'admin.py',
        'from django.contrib import admin\n'
    )
    
    # 3. apps.py
    apps_content = f"""from django.apps import AppConfig

class {app_name.capitalize()}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
"""
    write_file(app_name, 'apps.py', apps_content)
    
    # 4. migrations/__init__.py
    write_file(os.path.join(app_name, 'migrations'), '__init__.py', '')
    
    # 5. models.py
    write_file(app_name, 'models.py',
        'from django.db import models\n'
    )
    
    # 6. tests.py
    tests_content = '''from django.test import TestCase

# Create your tests here.
'''
    write_file(app_name, 'tests.py', tests_content)
    
    # 7. views.py
    views_content = '''from django.shortcuts import render

# Create your views here.
'''
    write_file(app_name, 'views.py', views_content)
    
    print(f"✅ Application '{app_name}' créée avec succès.")

def write_file(base_dir, filename, content):
    """Crée un fichier avec du contenu"""
    full_path = os.path.join(base_dir, filename)
    with open(full_path, 'w', encoding='utf-8') as f:
        f.write(content)

def main():
    """Point d'entrée pour la ligne de commande"""
    if len(sys.argv) < 2:
        print("Usage: create-app <app_name>")
        print("Exemple: create-app blog")
        sys.exit(1)
    
    app_name = sys.argv[1]
    create_app(app_name)