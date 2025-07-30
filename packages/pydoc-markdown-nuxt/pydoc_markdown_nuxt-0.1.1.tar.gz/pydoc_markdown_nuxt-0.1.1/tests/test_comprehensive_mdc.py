"""
Test comprehensive MDC processing with pytest.
"""

from pydoc_markdown_nuxt.renderer import MDCMarkdownRenderer


def test_comprehensive_mdc():
    """Test comprehensive MDC processing."""
    # Create a comprehensive docstring for testing
    comprehensive_docstring = """
    A comprehensive function to demonstrate all MDC features.
    
    **Arguments**:
    
    - `param1` - The first parameter
    - `param2: str` - The second parameter with type
    - `param3: int` - The third parameter with type
    
    **Returns**:
    
    dict: A dictionary containing results
    
    **Examples**:
    
    ```python
    result = comprehensive_function("test", 42)
    print(result)
    ```
    
    **Note**:
    
    This is an important note about the function.
    
    **Warning**:
    
    Be careful when using this function.
    
    **Raises**:
    
    - `ValueError` - If parameters are invalid
    - `TypeError` - If wrong types are provided
    """

    # Create MDC renderer
    renderer = MDCMarkdownRenderer(
        use_mdc=True,
        mdc_components={
            "arguments": "UArguments",
            "returns": "UReturns",
            "examples": "UCodeGroup",
            "notes": "UAlert",
            "warnings": "UAlert",
            "raises": "UCallout",
            "code_block": "UCodeGroup",
        },
    )

    # Process the docstring
    result = renderer._convert_arguments_to_mdc(comprehensive_docstring)

    # Assert expected components
    assert "::u-arguments" in result
    assert "param1" in result
    assert "param2" in result
    assert "param3" in result
