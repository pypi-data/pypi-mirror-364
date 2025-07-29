"""
htmlrunner - A simple package to run local HTML files.
"""
from .main import HtmlRunner

# Create a singleton instance to be used for running the HTML server.
# This allows users to import htmlrunner and use htmlrunner.htmlrun directly.
htmlrun = HtmlRunner()
