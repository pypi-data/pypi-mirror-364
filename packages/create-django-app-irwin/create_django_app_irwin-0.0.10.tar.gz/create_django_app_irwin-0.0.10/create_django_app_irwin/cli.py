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
    
    # Création des dossiers
    os.makedirs(app_name)
    os.makedirs(os.path.join(app_name, 'migrations'))
    os.makedirs(os.path.join(app_name, 'views'))
    os.makedirs(os.path.join(app_name, 'models'))
    os.makedirs(os.path.join(app_name, 'templates', app_name))  # AJOUTÉ
    os.makedirs(os.path.join(app_name, 'static', app_name))     # AJOUTÉ
    
    # 1. __init__.py
    write_file(app_name, '__init__.py', '')
    
    # 2. admin.py
    write_file(app_name, 'admin.py', 'from django.contrib import admin\n')
    
    # 3. urls.py
    write_file(app_name, 'urls.py', '')
    
    # 4. apps.py
    class_name = to_camel_case(app_name)
    apps_content = f"""from django.apps import AppConfig

class {class_name}Config(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = '{app_name}'
"""
    write_file(app_name, 'apps.py', apps_content)
    
    # 5. migrations/__init__.py
    write_file(os.path.join(app_name, 'migrations'), '__init__.py', '')
    
    # 6. models/__init__.py
    write_file(os.path.join(app_name, 'models'), '__init__.py', '')
    
    # 7. views/__init__.py
    write_file(os.path.join(app_name, 'views'), '__init__.py', '')
    
    # 8. tests.py
    tests_content = '''from django.test import TestCase

# Create your tests here.
'''
    write_file(app_name, 'tests.py', tests_content)
    
    # 9. templates/mon_app/my_template.html (AJOUTÉ)
    write_file(os.path.join(app_name, 'templates', app_name), 'my_template.html', '<!-- Template HTML -->')
    
    # 10. static/mon_app/style.css (AJOUTÉ)
    write_file(os.path.join(app_name, 'static', app_name), 'style.css', '/* CSS */')
    
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