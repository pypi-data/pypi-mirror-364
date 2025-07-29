"""Configuration file for the Sphinx documentation builder."""

import os
import sys
from datetime import datetime

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath('../..'))

# Project information
project = 'lcvtoolbox'
copyright = f'{datetime.now().year}, Logiroad'
author = 'Logiroad'

# Import the version from the package
import lcvtoolbox
release = lcvtoolbox.__version__
version = '.'.join(release.split('.')[:2])

# General configuration
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.coverage',
    'sphinx.ext.doctest',
    'sphinx.ext.autosummary',
    'sphinx.ext.githubpages',
    'sphinx_autodoc_typehints',
    'sphinx_copybutton',
    'myst_parser',
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = []

# The suffix(es) of source filenames.
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document.
master_doc = 'index'

# Autodoc configuration
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Autosummary configuration
autosummary_generate = True
autosummary_imported_members = True

# Napoleon settings for Google and NumPy style docstrings
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = False
napoleon_use_admonition_for_notes = False
napoleon_use_admonition_for_references = False
napoleon_use_ivar = False
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_preprocess_types = False
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Type hints configuration
typehints_fully_qualified = False
always_document_param_types = True
typehints_document_rtype = True

# Intersphinx mapping
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
    'pandas': ('https://pandas.pydata.org/docs/', None),
    'PIL': ('https://pillow.readthedocs.io/en/stable/', None),
}

# HTML output configuration
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']
html_theme_options = {
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': False,
    'style_nav_header_background': '#2980B9',
    # Toc options
    'collapse_navigation': True,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False
}

# Copy button configuration
copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True

# LaTeX output configuration
latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

# Grouping the document tree into LaTeX files
latex_documents = [
    (master_doc, 'lcvtoolbox.tex', 'lcvtoolbox Documentation',
     'Logiroad', 'manual'),
]

# One entry per manual page
man_pages = [
    (master_doc, 'lcvtoolbox', 'lcvtoolbox Documentation',
     [author], 1)
]

# Grouping the document tree into Texinfo files
texinfo_documents = [
    (master_doc, 'lcvtoolbox', 'lcvtoolbox Documentation',
     author, 'lcvtoolbox', 'Computer vision toolbox for road infrastructure analysis',
     'Miscellaneous'),
]

# Epub output configuration
epub_title = project
epub_exclude_files = ['search.html']

# MyST parser configuration
myst_enable_extensions = [
    "amsmath",
    "colon_fence",
    "deflist",
    "dollarmath",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# Suppress specific warnings
suppress_warnings = ['autosummary', 'autosummary.import_cycle']

# Add any custom CSS files
def setup(app):
    app.add_css_file('custom.css')
