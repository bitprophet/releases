from datetime import datetime
import os
import sys

import sphinx_rtd_theme


extensions = []
templates_path = ['_templates']
source_suffix = '.rst'
master_doc = 'index'

project = u'Releases'
year = datetime.now().year
copyright = u'%d Jeff Forcier' % year

# Ensure project directory is on PYTHONPATH for version, autodoc access
sys.path.insert(0, os.path.abspath(os.path.join(os.getcwd(), '..')))

exclude_patterns = ['_build']

# RTD theme
html_theme = "sphinx_rtd_theme"
html_theme_path = [sphinx_rtd_theme.get_html_theme_path()]

# Dogfood
extensions.append('releases')
releases_github_path = 'bitprophet/releases'
