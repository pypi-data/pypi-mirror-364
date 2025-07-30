"""
pydoc-markdown-nuxt: A Nuxt.js renderer for pydoc-markdown

This package provides a renderer for pydoc-markdown that generates documentation
following the Nuxt Content and MDC (Markdown Components) structure.
"""

__version__ = "0.1.1"
__author__ = "Uriel Curiel"
__email__ = "urielcuriel@outlook.com"

from .renderer import NuxtPage, NuxtRenderer
from .utils import (
    NuxtContentHelper,
    create_api_overview_table,
    create_mdc_alert,
    create_mdc_code_group,
    create_mdc_tabs,
    create_navigation_entry,
    enhance_frontmatter_for_nuxt,
    format_python_signature_for_mdc,
    generate_api_breadcrumbs,
)

__all__ = [
    "NuxtRenderer",
    "NuxtPage",
    "create_mdc_alert",
    "create_mdc_code_group",
    "create_mdc_tabs",
    "create_navigation_entry",
    "enhance_frontmatter_for_nuxt",
    "generate_api_breadcrumbs",
    "format_python_signature_for_mdc",
    "create_api_overview_table",
    "NuxtContentHelper",
]
