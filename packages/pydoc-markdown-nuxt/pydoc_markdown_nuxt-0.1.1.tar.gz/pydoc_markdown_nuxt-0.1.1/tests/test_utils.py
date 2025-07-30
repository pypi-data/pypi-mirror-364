"""
Test utility functions with pytest.
"""

import pytest

from pydoc_markdown_nuxt.utils import (
    create_mdc_alert,
    create_mdc_code_group,
    create_mdc_tabs,
    create_navigation_entry,
    enhance_frontmatter_for_nuxt,
    generate_api_breadcrumbs,
)


@pytest.mark.unit
def test_mdc_alert():
    """Test MDC alert creation utility."""
    # Test basic alert
    alert = create_mdc_alert("This is important information", "warning", "Important")
    expected_alert = '::alert{type="warning" title="Important"}\nThis is important information\n::'
    assert alert == expected_alert

    # Test without title
    alert = create_mdc_alert("Some info", "info")
    expected_alert = '::alert{type="info"}\nSome info\n::'
    assert alert == expected_alert

    # Test with custom component name
    alert = create_mdc_alert("Custom alert", "error", "Error", "u-alert")
    expected_alert = '::u-alert{type="error" title="Error"}\nCustom alert\n::'
    assert alert == expected_alert


@pytest.mark.unit
def test_mdc_code_group():
    """Test MDC code group creation utility."""
    # Test with multiple code blocks
    code_blocks = [
        {"language": "python", "filename": "example.py", "code": "print('Hello, World!')"},
        {"language": "javascript", "filename": "example.js", "code": "console.log('Hello, World!');"},
    ]
    code_group = create_mdc_code_group(code_blocks)

    assert "::code-group" in code_group
    assert "```python [example.py]" in code_group
    assert "```javascript [example.js]" in code_group
    assert "print('Hello, World!')" in code_group
    assert "console.log('Hello, World!');" in code_group

    # Test with custom component name
    code_group = create_mdc_code_group(code_blocks, "u-code-group")
    assert "::u-code-group" in code_group


@pytest.mark.unit
def test_mdc_tabs():
    """Test MDC tabs creation utility."""
    # Test with multiple tabs
    tabs = [{"title": "Tab 1", "content": "Content 1"}, {"title": "Tab 2", "content": "Content 2"}]
    tab_component = create_mdc_tabs(tabs)

    assert "::tabs" in tab_component
    assert 'label="Tab 1"' in tab_component
    assert 'label="Tab 2"' in tab_component
    assert "Content 1" in tab_component
    assert "Content 2" in tab_component

    # Test with custom component name
    tab_component = create_mdc_tabs(tabs, "u-tabs")
    assert "::u-tabs" in tab_component


@pytest.mark.unit
def test_navigation_entry():
    """Test navigation entry creation utility."""
    # Test with all properties
    nav_entry = create_navigation_entry(
        "API Reference",
        "/docs/api",
        icon="heroicons:code-bracket",
        badge="New",
        description="Complete API documentation",
    )

    assert nav_entry["title"] == "API Reference"
    assert nav_entry["to"] == "/docs/api"
    assert nav_entry["icon"] == "heroicons:code-bracket"
    assert nav_entry["badge"] == "New"
    assert nav_entry["description"] == "Complete API documentation"

    # Test with minimal properties
    nav_entry = create_navigation_entry("Simple", "/simple")
    assert nav_entry["title"] == "Simple"
    assert nav_entry["to"] == "/simple"
    assert "icon" not in nav_entry


@pytest.mark.unit
def test_frontmatter_enhancement():
    """Test frontmatter enhancement for Nuxt."""
    # Test basic frontmatter
    basic_frontmatter = {"title": "My Page"}
    enhanced = enhance_frontmatter_for_nuxt(basic_frontmatter, "reference")

    assert enhanced["title"] == "My Page"
    assert enhanced["layout"] == "docs"  # Default value added
    assert enhanced["navigation"]  # Default value added

    # Test merging with existing values
    custom_frontmatter = {"title": "Custom Page", "layout": "custom", "navigation": False}
    enhanced = enhance_frontmatter_for_nuxt(custom_frontmatter, "reference")

    assert enhanced["title"] == "Custom Page"
    assert enhanced["layout"] == "custom"  # Preserved
    assert not enhanced["navigation"]  # Preserved


@pytest.mark.unit
def test_api_breadcrumbs():
    """Test API breadcrumbs generation."""
    # Test for a nested module
    breadcrumbs = generate_api_breadcrumbs("module.submodule.Class.method", "/docs/api")

    assert len(breadcrumbs) == 4
    assert breadcrumbs[0]["title"] == "module"
    assert breadcrumbs[0]["to"] == "/docs/api/module"
    assert breadcrumbs[3]["title"] == "method"

    # Test with base URL
    breadcrumbs = generate_api_breadcrumbs("Class.method", "/custom/path")

    assert len(breadcrumbs) == 2
    assert breadcrumbs[0]["to"].startswith("/custom/path")
