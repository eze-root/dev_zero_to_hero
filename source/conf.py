# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Develop from Zero to Hero'
copyright = '2024, ezelab'
author = 'ezelab'
release = '0.0.1'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
  "myst_parser",
  "sphinx.ext.autodoc",
  "sphinx.ext.intersphinx",
  "sphinx.ext.extlinks",
  "sphinx.ext.todo",
  "sphinx.ext.viewcode",
  "sphinxcontrib.mermaid",
  "sphinxemoji.sphinxemoji",
  "sphinx_copybutton",
  "sphinx_design",
  "sphinx_exercise",
  "sphinx_comments"
]

myst_enable_extensions=[
    "amsmath",
    "attrs_inline",
    "colon_fence",
    "deflist",
    "dollarmath",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "strikethrough",
    "substitution",
    "tasklist",

]

myst_words_per_minute = 10

comments_config = {
   "utterances": {
      "repo": "eze-root/dev_zero_to_hero",
      "optional": "config",
   }
}


html_context = {
    "source_type": "github",
    "source_user": "eze-root",
    "source_repo": "dev_zero_to_hero",
    "source_version": "main",
    "source_docs_path": "/source/",
}


templates_path = ['_templates']
exclude_patterns = ['build', 'Thumbs.db', '.DS_Store']

language = 'zh'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'shibuya'
html_static_path = ['_static']

html_title = 'Develop from Zero to Hero'

html_theme_options = {
    'accent_color': 'tomato',
    'color_mode': 'auto',
    'dark_code': True,
    'globaltoc_expand_depth': 1,
    'toctree_maxdepth': 3,
    'github_url': 'https://github.com/eze-root/dev_zero_to_hero',
    'show_ai_links': False,
}


html_css_files = [
    'https://cdn.jsdelivr.net/npm/source-sans@3.52.0/source-sans-3VF.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css',
    'css/course.css',
]

latex_engine = 'xelatex'
latex_elements = {
    'passoptionstopackages': r'''
\PassOptionsToPackage{svgnames}{xcolor}
''',
    'fontpkg': r'''
\usepackage{fontspec}
''',
    'preamble': r'''
\usepackage[titles]{tocloft}
\cftsetpnumwidth {1.25cm}\cftsetrmarg{1.5cm}
\setlength{\cftchapnumwidth}{0.75cm}
\setlength{\cftsecindent}{\cftchapnumwidth}
\setlength{\cftsecnumwidth}{1.25cm}
''',
    'sphinxsetup': 'TitleColor=DarkGoldenrod',
    'fncychap': r'\usepackage[Bjornstrup]{fncychap}',
    'printindex': r'\footnotesize\raggedright\printindex',
}
latex_show_urls = 'footnote'
