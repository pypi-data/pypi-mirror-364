"""
Test NuxtContentResolver functionality with pytest.
"""

import docspec
import pytest

from pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer, NuxtContentResolver


@pytest.mark.unit
def test_nuxt_content_resolver():
    """Test that the NuxtContentResolver correctly resolves references."""

    # Create a resolver with a base path
    resolver = NuxtContentResolver("docs/api")

    # Create a mock API object hierarchy for testing
    root_module = docspec.Module(
        name="mypackage",
        location=docspec.Location(filename="mypackage/__init__.py", lineno=1),
        docstring=None,
        members=[],
    )

    sub_module = docspec.Module(
        name="core", location=docspec.Location(filename="mypackage/core.py", lineno=1), docstring=None, members=[]
    )

    test_class = docspec.Class(
        name="DataProcessor",
        location=docspec.Location(filename="mypackage/core.py", lineno=10),
        docstring=None,
        members=[],
        metaclass=None,
        bases=[],
        decorations=[],
    )

    test_method = docspec.Function(
        name="process",
        location=docspec.Location(filename="mypackage/core.py", lineno=20),
        docstring=None,
        modifiers=None,
        args=[],
        return_type=None,
        decorations=[],
    )

    # Build the hierarchy manually
    sub_module.parent = root_module
    test_class.parent = sub_module
    test_method.parent = test_class

    root_module.members = [sub_module]
    sub_module.members = [test_class]
    test_class.members = [test_method]

    # Test basic reference resolution
    result = resolver.resolve_ref(root_module, "mypackage.core.DataProcessor")
    expected = "/docs/api/mypackage/core/dataprocessor"
    assert result == expected

    # Test object ID generation
    object_id = resolver.generate_object_id(test_method)
    expected_id = "mypackage.core.DataProcessor.process"
    assert object_id == expected_id


@pytest.mark.unit
def test_mdc_markdown_renderer_with_resolver():
    """Test that MDCMarkdownRenderer works with NuxtContentResolver."""

    # Create renderer with content resolver
    renderer = MDCMarkdownRenderer(content_directory="content/docs", use_mdc=True)

    # Test that the resolver is correctly initialized
    assert isinstance(renderer._resolver, NuxtContentResolver)
    assert renderer._resolver.base_path == "content/docs"

    # Test docstring processing with cross-references
    docstring_with_refs = """
    A test function that processes data.
    
    **Arguments**:
    
    - `data: str` - The input data to process
    - `config: Config` - Configuration object
    
    **Returns**:
    
    Processed data as a string.
    
    See also: mypackage.core.Config for configuration details.
    """

    # Process the docstring
    result = renderer._process_docstring_for_mdc(docstring_with_refs)

    # Verify MDC conversion happened
    assert "::u-arguments" in result
    assert "name: data" in result
    assert "type: str" in result
    assert "name: config" in result
    assert "type: Config" in result
