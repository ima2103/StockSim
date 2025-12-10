# conf_clean.py (dans docs/)

import os
import sys
# Ajout du chemin parent (votre dossier StockSim)
sys.path.insert(0, os.path.abspath('..'))


project = 'StockSim'
copyright = '2025, Projet Markoviens'
author = '(Guemeni et Massudom/ Groupe 12)'
release = '0.1.0'


# --- La section critique ---
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx_rtd_theme',
]
# --- Fin de la section critique ---


templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']
html_theme = 'sphinx_rtd_theme'