"""
Test MDC arguments conversion with pytest.
"""

from pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer


def test_mdc_conversion(sample_arguments_docstring):
    """Test that MDC arguments are converted correctly."""
    # Create MDC renderer
    renderer = MDCMarkdownRenderer(use_mdc=True, mdc_components={"arguments": "UArguments"})

    # Process the docstring
    result = renderer._convert_arguments_to_mdc(sample_arguments_docstring)

    # Assert the expected results
    assert "::u-arguments" in result
    assert "name: param1" in result
    assert "name: param2" in result
    assert "type: str" in result
    assert "name: param3" in result
    assert "type: int" in result
    assert "**Arguments**:" not in result
