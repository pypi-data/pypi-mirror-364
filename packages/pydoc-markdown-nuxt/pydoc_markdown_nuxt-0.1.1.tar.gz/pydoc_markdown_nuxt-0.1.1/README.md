# pydoc-markdown-nuxt

A pydoc-markdown renderer for generating documentation compatible with Nuxt Content and MDC (Markdown Components).

## Overview

`pydoc-markdown-nuxt` extends [pydoc-markdown](https://github.com/NiklasRosenstein/pydoc-markdown) with a renderer that generates Markdown files following the [Nuxt Content](https://content.nuxtjs.org/) structure and conventions. This allows you to seamlessly integrate Python API documentation into Nuxt.js websites.

## Features

- **Nuxt Content Compatible**: Generates Markdown files with YAML frontmatter that work with Nuxt Content's file-based routing
- **Flexible Directory Structure**: Configure custom directory structures and file organization
- **YAML Frontmatter**: Full control over page metadata through configurable frontmatter
- **MDC Support**: Ready for MDC (Markdown Components) syntax extensions
- **Clean Integration**: Works with existing pydoc-markdown configurations and processors

## Installation

```bash
pip install pydoc-markdown-nuxt
```

## Quick Start

Create a `pydoc-markdown.yml` configuration file:

```yaml
loaders:
  - type: python
    search_path: [src]

renderers:
  - type: nuxt
    content_directory: content/docs
    default_frontmatter:
      layout: docs
      navigation: true
    pages:
      - title: API Documentation
        contents:
          - '*'
```

Then run:

```bash
pydoc-markdown
```

This will generate Nuxt Content compatible Markdown files in the `content/docs` directory.

## Configuration

### Basic Options

- `content_directory`: Directory where content files are generated (default: `content`)
- `clean_render`: Whether to clean previous files before rendering (default: `true`)
- `default_frontmatter`: Default YAML frontmatter applied to all pages
- `use_mdc`: Enable MDC syntax features (default: `true`)
- `base_url`: Base URL for documentation (default: `/`)

### Page Configuration

Pages support all standard pydoc-markdown page options plus:

- `frontmatter`: Custom YAML frontmatter for the page
- `directory`: Custom subdirectory for the page
- `extension`: File extension (default: `.md`)

### Example Configuration

```yaml
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
        directory: reference
        frontmatter:
          description: "Complete API reference"
          icon: "code"
        contents:
          - mypackage.*
```

## Generated Output

The renderer generates Markdown files with YAML frontmatter:

```markdown
---
title: API Documentation
layout: docs
navigation: true
description: Complete API reference
icon: code
---

# MyClass

A sample class for demonstration.

## Methods

### my_method(param1, param2='default')

A sample method that does something useful.

**Arguments:**
- `param1`: First parameter
- `param2`: Second parameter with default value

**Returns:**
Something useful
```

## Integration with Nuxt Content

The generated files work seamlessly with Nuxt Content:

1. **File-based Routing**: Files in `content/` automatically become pages
2. **Navigation**: Use frontmatter to control navigation appearance
3. **Layouts**: Specify custom layouts through frontmatter
4. **Metadata**: Rich metadata support for SEO and organization

## MDC Support

When `use_mdc: true`, the renderer is ready for MDC enhancements:

```markdown
::alert{type="info"}
This is an info alert using MDC syntax
::

::code-group
```python
# Python example
def hello():
    return "Hello, World!"
```
::
```

## Development

To contribute to this project:

```bash
git clone https://github.com/UrielCuriel/pydoc-markdown-nuxt
cd pydoc-markdown-nuxt
pip install -e .
```

Run tests:

```bash
python test_renderer.py
```

## License

MIT License - see LICENSE file for details.
