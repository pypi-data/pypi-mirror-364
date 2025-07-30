"""
Test configuration handling with pytest.
"""

import pytest
import yaml
from pydoc_markdown.interfaces import Context

from pydoc_markdown_nuxt.renderer import NuxtPage, NuxtRenderer


@pytest.fixture
def test_config():
    """Load test configuration from file."""
    with open("config-examples/pydoc-markdown.test.yml", "r") as f:
        return yaml.safe_load(f)


@pytest.mark.unit
def test_yaml_configuration(test_config: yaml.Any):
    """Test loading and using our renderer with a YAML configuration."""
    # Extract renderer configuration
    renderer_config = test_config["renderer"]

    # Create renderer from configuration
    renderer = NuxtRenderer(
        content_directory=renderer_config.get("content_directory", "content"),
        default_frontmatter=renderer_config.get("default_frontmatter", {}),
        use_mdc=renderer_config.get("use_mdc", True),
        clean_render=renderer_config.get("clean_render", True),
    )

    # Add pages from configuration
    for page_config in renderer_config.get("pages", []):
        page = NuxtPage(
            title=page_config["title"],
            name=page_config.get("name"),
            frontmatter=page_config.get("frontmatter", {}),
            directory=page_config.get("directory"),
            contents=page_config.get("contents"),
        )
        renderer.pages.append(page)

    # Verify renderer configuration
    assert renderer.content_directory == renderer_config["content_directory"]
    assert renderer.default_frontmatter == renderer_config.get("default_frontmatter", {})
    assert len(renderer.pages) == len(renderer_config.get("pages", []))


@pytest.mark.integration
def test_advanced_configuration(temp_test_dir: Any):
    """Test a more complex configuration with multiple pages and directories."""
    config = {
        "content_directory": str(temp_test_dir),
        "use_mdc": True,
        "default_frontmatter": {
            "layout": "docs",
            "navigation": {
                "title": "Documentation",
                "icon": "book",
            },
        },
        "pages": [
            {"title": "Home", "name": "index", "frontmatter": {"hero": True, "description": "Welcome page"}},
            {
                "title": "API Reference",
                "name": "api",
                "directory": "reference",
                "frontmatter": {"category": "API", "icon": "code"},
            },
            {
                "title": "Examples",
                "name": "examples",
                "directory": "guides",
                "frontmatter": {"category": "Guide", "icon": "lightbulb"},
            },
        ],
    }

    default_frontmatter = config.get("default_frontmatter", {})
    if not isinstance(default_frontmatter, dict):
        default_frontmatter = {}

    use_mdc = bool(config.get("use_mdc", True))
    renderer = NuxtRenderer(
        content_directory=str(config["content_directory"]),
        default_frontmatter=default_frontmatter,
        use_mdc=use_mdc,
    )

    pages = config.get("pages", [])
    if not isinstance(pages, list):
        pages = []
    for page_config in pages:
        frontmatter: dict[str, bool | str] | dict[str, str] | str = page_config.get("frontmatter", {})
        if not isinstance(frontmatter, dict):
            frontmatter = {}
        page: NuxtPage = NuxtPage(
            title=str(page_config["title"]),
            name=str(page_config.get("name")) if page_config.get("name") is not None else None,
            frontmatter=frontmatter,
            directory=page_config.get("directory"),  # Don't convert None to string
        )
        renderer.pages.append(page)

    # Initialize the renderer
    context = Context(str(temp_test_dir))
    renderer.init(context)

    # Render with empty modules
    renderer.render([])

    # Verify files were created with correct structure
    index_path = temp_test_dir / "index.md"
    api_path = temp_test_dir / "reference" / "api.md"
    examples_path = temp_test_dir / "guides" / "examples.md"

    assert index_path.exists()
    assert api_path.exists()
    assert examples_path.exists()

    # Verify frontmatter was correctly applied
    with open(index_path, "r") as f:
        content = f.read()
        assert "layout: docs" in content
        assert "hero: true" in content
