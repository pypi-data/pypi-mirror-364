"""
Test MDC arguments generation with pytest.
"""

import docspec
import pytest

from pydoc_markdown_nuxt.renderer import NuxtPage, NuxtRenderer


@pytest.fixture
def mock_function():
    """Create a sample docspec function for testing."""
    return docspec.Function(
        name="test_function",
        location=docspec.Location(filename="test.py", lineno=1),
        modifiers=None,
        return_type=None,
        decorations=None,
        docstring=docspec.Docstring(
            location=docspec.Location(filename="test.py", lineno=1),
            content="""
        A test function to demonstrate argument rendering.
        
        **Arguments**:
        
        - `param1` - The first parameter
        - `param2: str` - The second parameter with type
        - `param3: int` - The third parameter with type
        
        **Returns**:
        
        Some return value
        """,
        ),
        args=[
            docspec.Argument(name="param1", type=None, location=docspec.Location(filename="test.py", lineno=1)),
            docspec.Argument(name="param2", type=None, location=docspec.Location(filename="test.py", lineno=1)),
            docspec.Argument(name="param3", type=None, location=docspec.Location(filename="test.py", lineno=1)),
        ],
    )


@pytest.fixture
def mock_module(mock_function):
    """Create a sample docspec module for testing."""
    return docspec.Module(
        name="test_module",
        location=docspec.Location(filename="test.py", lineno=1),
        docstring=docspec.Docstring(location=docspec.Location(filename="test.py", lineno=1), content="Test module"),
        members=[mock_function],
    )


@pytest.mark.integration
def test_mdc_arguments(temp_test_dir, mock_module):
    """Test that MDC arguments are generated correctly."""
    # Import Pages class
    from pydoc_markdown.util.pages import Pages

    # Create renderer configuration
    pages = Pages()
    pages.append(NuxtPage(title="Test", name="test", source="README.md", contents=["test_module"]))

    renderer = NuxtRenderer(
        content_directory=str(temp_test_dir), use_mdc=True, mdc_components={"arguments": "UArguments"}, pages=pages
    )

    # Create a simple README file for testing
    readme_path = temp_test_dir / "README.md"
    readme_path.write_text("# Test\n\nThis is a test README.")

    # Create a Context object
    from pydoc_markdown.interfaces import Context

    context = Context(str(temp_test_dir))

    # Initialize the renderer
    renderer.init(context)

    # Render the module
    renderer.render([mock_module])

    # Check that the output file exists
    output_file = temp_test_dir / "test.md"
    assert output_file.exists()

    # Check that the content contains MDC arguments
    content = output_file.read_text()
    assert "::u-arguments" in content
    assert "name: param1" in content
    assert "name: param2" in content
    assert "type: str" in content
    assert "name: param3" in content
    assert "type: int" in content
