# create_django_app_irwin

📦 Génère automatiquement la structure de base d'une application Django avec une seule commande CLI (`create-app`), comme `django-admin startapp`.

## 🚀 Fonctionnalités

- ✅ Crée tous les fichiers essentiels : `models.py`, `views.py`, `apps.py`, `admin.py`, `tests.py`, `migrations/`, etc.
- ✅ Remplit chaque fichier avec le contenu minimal utilisé par Django
- ✅ Interface en ligne de commande simple et intuitive
- ✅ Compatible avec tous les projets Django modernes

## 📦 Installation

```bash
pip install create_django_app_irwin
```

## 💡 Utilisation

```bash
# Créer une nouvelle application Django
create-app blog

# Créer une application avec un nom différent
create-app mon_ecommerce
```

## 📁 Structure générée

Après avoir exécuté `create-app blog`, vous obtiendrez :

```
blog/
├── __init__.py
├── admin.py
├── apps.py
├── models.py
├── tests.py
├── views.py
└── migrations/
    └── __init__.py
```

## 🛠️ Prérequis

- Python 3.7+
- Django 3.2+ (installé automatiquement)

## 🤝 Contribution

Les contributions sont les bienvenues ! N'hésitez pas à :
- Signaler des bugs
- Proposer de nouvelles fonctionnalités
- Soumettre des pull requests

## 📄 Licence

MIT License - voir le fichier (LICENSE) pour plus de détails.


## 🔗 Liens utiles

- [Documentation Django](https://docs.djangoproject.com/)
- [PyPI Package](https://pypi.org/project/create_django_app_irwin/)