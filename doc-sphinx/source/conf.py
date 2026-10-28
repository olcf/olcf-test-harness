# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'OLCF Test Harness'
copyright = '2026, ORNL'
author = 'ORNL'
release = '4.0.0-alpha'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    "sphinx_design",
    "sphinx_multiversion",
]

templates_path = ['_templates']
exclude_patterns = []



# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = "sphinx_rtd_theme"
html_static_path = ["_static"]
html_logo = "_static/images/olcf_logo.png"
html_theme_options = {
    "collapse_navigation": False,
    "style_external_links": True,
    "style_nav_header_background": "#efefef",
    "logo_only": True,
}
html_css_files = [
    "custom.css",
]

# -- Options for sphinx-multiversion -----------------------------------------

smv_tag_whitelist = r"^v\d+\.\d+$"
smv_branch_whitelist = r"^devel$"
