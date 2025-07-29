# setup.py

from setuptools import setup, find_packages

setup(
    name='create_django_app_irwin',  # ← nom unique
    version='0.0.6',  # ← incrémente bien à chaque build
    packages=find_packages(),
    install_requires=[],
    entry_points={
        'console_scripts': [
            'create-app=create_django_app_irwin.cli:main',
        ],
    },
    author='DJRIGA IRWIN JESSY',
    author_email='irwindjriga@gmail.com',
    description='Génère une structure d’app Django automatiquement',
    long_description=open('README.md', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    license='MIT',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
