# setup.py

from setuptools import setup, find_packages

# Lisez le contenu du README pour la description longue
try:
    with open('README.md', encoding='utf-8') as f:
        long_description = f.read()
except FileNotFoundError:
    long_description = 'Simulation et optimisation de la gestion de stock empilé (Projet Markoviens).'

setup(
    name='StockSim',
    version='0.1.0',

    # Trouver automatiquement le dossier de package "StockSim"
    packages=find_packages(),

    # Métadonnées du projet
    description='Simulation et optimisation de la gestion de stock empilé (Projet Markoviens).',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Guemeni et Massudom / Équipe 12',
    author_email='contact@votre-email.com',
    license='MIT',  # Ou une autre licence de votre choix

    # Dépendances requises pour l'exécution
    install_requires=[
        'numpy>=1.20',
        # 'pandas>=1.3', # Si vous utilisez pandas
        'streamlit>=1.0',
    ],

    # Dépendances requises pour le développement et la documentation
    extras_require={
        'dev': [
            'pytest>=6.2',
            'sphinx>=4.0',
            'sphinx-rtd-theme',
            'setuptools'  # Assure que les outils de packaging sont disponibles
        ]
    },

    python_requires='>=3.8',

    # Classificateurs (aide les utilisateurs à trouver votre package sur PyPI)
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Simulation',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
    ],
)