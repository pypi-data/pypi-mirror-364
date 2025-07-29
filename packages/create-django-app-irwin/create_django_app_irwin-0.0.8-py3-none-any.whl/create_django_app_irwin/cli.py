# create_django_app_irwin/cli.py
import os
import sys

def to_camel_case(snake_str):
    """Convertit un nom snake_case en CamelCase"""
    return ''.join(word.capitalize() for word in snake_str.split('_'))

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

    # 3. urls.py
    write_file(app_name, 'urls.py','')
    
    # 3. apps.py
    class_name = to_camel_case(app_name)
    apps_content = f"""from django.apps import AppConfig
    

class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
    
"""
    write_file(app_name, 'apps.py', apps_content)
    
    # 4. migrations/__init__.py
    write_file(os.path.join(app_name, 'migrations'), '__init__.py', '')
    
    # 5. models.py
    write_file(os.path.join(app_name, 'models.py'), '__init__.py', '')

    # 6. views.py
    write_file(os.path.join(app_name, 'views.py'), '__init__.py', '')
    
    # 6. tests.py
    tests_content = '''from django.test import TestCase

# Create your tests here.
'''
    
    # 7. views.py

# Create your views here.
   
    write_file(os.path.join(app_name, 'views.py'), '__init__.py', '')
    
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