"""
Example configurations for pydoc-markdown-nuxt
"""

# Basic example configuration
BASIC_CONFIG = """
# Basic pydoc-markdown-nuxt configuration
loaders:
  - type: python
    search_path: [src]

renderers:
  - type: nuxt
    content_directory: content/docs
    default_frontmatter:
      layout: default
      navigation: true
    pages:
      - title: API Documentation
        contents:
          - '*'
"""

# Advanced example with multiple pages and custom frontmatter
ADVANCED_CONFIG = """
# Advanced pydoc-markdown-nuxt configuration
loaders:
  - type: python
    search_path: [src]

processors:
  - type: filter
    expression: not name.startswith('_')
  - type: smart
  - type: crossref

renderers:
  - type: nuxt
    content_directory: content/docs
    use_mdc: true
    base_url: /docs/
    default_frontmatter:
      layout: docs
      navigation: true
      sidebar: true
    pages:
      - title: Home
        name: index
        source: README.md
        frontmatter:
          description: "Welcome to our API documentation"
          icon: "home"
      - title: Getting Started
        name: getting-started
        source: docs/getting-started.md
        frontmatter:
          description: "Quick start guide"
          icon: "rocket"
      - title: API Reference
        name: api
        frontmatter:
          description: "Complete API reference"
          icon: "code"
        contents:
          - mypackage.*
      - title: Examples
        name: examples
        directory: examples
        frontmatter:
          description: "Usage examples"
          icon: "lightbulb"
        contents:
          - examples.*
"""

# Configuration with MDC components
MDC_CONFIG = """
# pydoc-markdown-nuxt with MDC components
loaders:
  - type: python
    search_path: [src]

processors:
  - type: filter
    expression: not name.startswith('_')
  - type: smart
  - type: crossref

renderers:
  - type: nuxt
    content_directory: content/docs
    use_mdc: true
    default_frontmatter:
      layout: docs
      navigation: true
    markdown:
      code_headers: true
      descriptive_class_title: true
      add_module_prefix: true
    pages:
      - title: API Documentation
        frontmatter:
          description: "Python API documentation with MDC components"
          category: "API"
        contents:
          - '*'
"""