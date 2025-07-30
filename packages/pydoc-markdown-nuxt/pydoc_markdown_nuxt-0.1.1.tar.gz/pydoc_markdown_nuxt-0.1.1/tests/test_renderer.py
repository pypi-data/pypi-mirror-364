"""
Test NuxtRenderer functionality with pytest.
"""

import pytest
from pydoc_markdown.interfaces import Context

from pydoc_markdown_nuxt.renderer import NuxtPage, NuxtRenderer


@pytest.mark.unit
def test_basic_page_rendering(temp_test_dir):
    """Test basic page rendering functionality without complex docspec objects."""
    # Set up the renderer
    renderer = NuxtRenderer(
        content_directory=str(temp_test_dir),
        default_frontmatter={
            "layout": "docs",
            "navigation": True,
        },
    )

    # Create a page configuration
    page = NuxtPage(
        title="API Documentation",
        name="api",
        frontmatter={"description": "API reference documentation", "category": "API"},
    )
    renderer.pages.append(page)

    # Initialize the renderer with context
    context = Context(str(temp_test_dir))
    renderer.init(context)

    # Render with empty modules list (just test the structure)
    renderer.render([])

    # Check that files were created
    output_file = temp_test_dir / "api.md"
    assert output_file.exists()

    # Verify content
    content = output_file.read_text()
    assert "title: API Documentation" in content
    assert "layout: docs" in content
    assert "navigation: true" in content
    assert "description: API reference documentation" in content
    assert "category: API" in content


@pytest.mark.unit
def test_frontmatter_merging(temp_test_dir):
    """Test that default and page-specific frontmatter are merged correctly."""
    # Set up renderer with default frontmatter
    renderer = NuxtRenderer(
        content_directory=str(temp_test_dir),
        default_frontmatter={"layout": "docs", "navigation": True, "sidebar": True},
    )

    # Create page with custom frontmatter
    page = NuxtPage(
        title="Custom Page",
        name="custom",
        frontmatter={
            "description": "Custom page description",
            "layout": "custom-layout",  # Should override default
            "toc": True,  # Should be added to default
        },
    )
    renderer.pages.append(page)

    # Initialize and render
    context = Context(str(temp_test_dir))
    renderer.init(context)
    renderer.render([])

    # Check output
    output_file = temp_test_dir / "custom.md"
    assert output_file.exists()

    # Verify merged frontmatter
    content = output_file.read_text()
    assert "title: Custom Page" in content
    assert "layout: custom-layout" in content  # Override works
    assert "navigation: true" in content  # Default preserved
    assert "sidebar: true" in content  # Default preserved
    assert "toc: true" in content  # Page-specific added
    assert "description: Custom page description" in content


@pytest.mark.unit
def test_directory_structure(temp_test_dir):
    """Test that pages can be rendered to custom directories."""
    # Set up renderer
    renderer = NuxtRenderer(content_directory=str(temp_test_dir), default_frontmatter={"layout": "docs"})

    # Create pages in different directories
    pages = [
        NuxtPage(title="Home", name="index"),
        NuxtPage(title="API", name="api", directory="reference"),
        NuxtPage(title="Examples", name="examples", directory="guides/tutorials"),
    ]

    for page in pages:
        renderer.pages.append(page)

    # Initialize and render
    context = Context(str(temp_test_dir))
    renderer.init(context)
    renderer.render([])

    # Verify directory structure
    assert (temp_test_dir / "index.md").exists()
    assert (temp_test_dir / "reference" / "api.md").exists()
    assert (temp_test_dir / "guides" / "tutorials" / "examples.md").exists()
