"""
Utility functions for working with Nuxt Content and MDC syntax.
"""

import re
from typing import Any, Dict, List, Optional


def _convert_to_kebab_case(component_name: str) -> str:
    """
    Convert component name to kebab-case following Nuxt MDC conventions.

    Examples:
        UAlert -> u-alert
        UCodeGroup -> u-code-group
        UPageHero -> u-page-hero
        CustomComponent -> custom-component
        u-alert -> u-alert (already in kebab-case)
    """
    # If already in kebab-case (contains hyphens), return as-is
    if "-" in component_name:
        return component_name.lower()

    # Convert PascalCase to kebab-case
    # Insert hyphens before uppercase letters (except the first one)
    kebab_case = re.sub(r"(?<!^)(?=[A-Z])", "-", component_name).lower()

    return kebab_case


def create_mdc_alert(content: str, type: str = "info", title: Optional[str] = None, component: str = "alert") -> str:
    """
    Create an MDC alert component.

    Args:
        content: The alert content
        type: Alert type (info, warning, error, success)
        title: Optional title for the alert
        component: Component name to use (default: alert)

    Returns:
        MDC alert syntax string
    """
    props = f'type="{type}"'
    if title:
        props += f' title="{title}"'

    # Convert component name to kebab-case
    component_name = _convert_to_kebab_case(component)

    return f"::{component_name}{{{props}}}\n{content}\n::"


def create_mdc_code_group(code_blocks: List[Dict[str, str]], component: str = "code-group") -> str:
    """
    Create an MDC code group with multiple code blocks.

    Args:
        code_blocks: List of dicts with 'language', 'filename', and 'code' keys
        component: Component name to use (default: code-group)

    Returns:
        MDC code group syntax string
    """
    # Convert component name to kebab-case
    component_name = _convert_to_kebab_case(component)

    result = f"::{component_name}\n"

    for block in code_blocks:
        lang = block.get("language", "text")
        filename = block.get("filename", "")
        code = block.get("code", "")

        if filename:
            result += f"```{lang} [{filename}]\n"
        else:
            result += f"```{lang}\n"

        result += f"{code}\n```\n"

    result += "::"
    return result


def create_mdc_tabs(tabs: List[Dict[str, str]], component: str = "tabs") -> str:
    """
    Create MDC tabs component.

    Args:
        tabs: List of dicts with 'title' and 'content' keys
        component: Component name to use (default: tabs)

    Returns:
        MDC tabs syntax string
    """
    # Convert component name to kebab-case
    component_name = _convert_to_kebab_case(component)

    result = f"::{component_name}\n"

    for tab in tabs:
        title = tab.get("title", "Tab")
        content = tab.get("content", "")

        result += f'  ::div{{label="{title}"}}\n'
        result += f"  {content}\n"
        result += "  ::\n"

    result += "::"
    return result


def create_mdc_variables(variables: List[Dict[str, str]], component: str = "UVariables") -> str:
    """
    Create an MDC variables component.

    Args:
        variables: List of dicts with 'name', 'type', and 'content' keys
        component: Component name to use (default: UVariables)

    Returns:
        MDC variables syntax string
    """
    # Convert component name to kebab-case
    component_name = _convert_to_kebab_case(component)

    # Build the frontmatter-style variables section
    variables_yaml = "---\nvariables:\n"
    for var in variables:
        name = var.get("name", "")
        type_info = var.get("type", "")
        content = var.get("content", "")

        variables_yaml += f"  - name: {name}\n"
        variables_yaml += f"    type: {type_info}\n"
        variables_yaml += f"    content: {content}\n"

    variables_yaml += "---"

    return f"::{component_name}\n{variables_yaml}\n::"


def create_mdc_arguments(arguments: List[Dict[str, str]], component: str = "UArguments") -> str:
    """
    Create an MDC arguments component.

    Args:
        arguments: List of dicts with 'name', 'type', and 'content' keys
        component: Component name to use (default: UArguments)

    Returns:
        MDC arguments syntax string
    """
    # Convert component name to kebab-case
    component_name = _convert_to_kebab_case(component)

    # Build the frontmatter-style arguments section
    arguments_yaml = "---\narguments:\n"
    for arg in arguments:
        name = arg.get("name", "")
        type_info = arg.get("type", "")
        content = arg.get("content", "")

        arguments_yaml += f"  - name: {name}\n"
        arguments_yaml += f"    type: {type_info}\n"
        arguments_yaml += f"    content: {content}\n"

    arguments_yaml += "---"

    return f"::{component_name}\n{arguments_yaml}\n::"


def create_variable_or_argument_component(
    items: List[Dict[str, str]], component_type: str = "variables", component: Optional[str] = None
) -> str:
    """
    Create either a variables or arguments MDC component.

    Args:
        items: List of dicts with 'name', 'type', and 'content' keys
        component_type: Either 'variables' or 'arguments'
        component: Component name to use (auto-detected if None)

    Returns:
        MDC component syntax string
    """
    if component is None:
        component = f"U{component_type.capitalize()}"

    if component_type.lower() == "variables":
        return create_mdc_variables(items, component)
    elif component_type.lower() == "arguments":
        return create_mdc_arguments(items, component)
    else:
        raise ValueError(f"Invalid component_type: {component_type}. Must be 'variables' or 'arguments'")


def create_navigation_entry(
    title: str, path: str, icon: Optional[str] = None, badge: Optional[str] = None, description: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create a navigation entry for Nuxt Content.

    Args:
        title: Navigation title
        path: Path to the page
        icon: Optional icon name
        badge: Optional badge text
        description: Optional description

    Returns:
        Navigation entry dictionary
    """
    entry = {"title": title, "to": path}

    if icon:
        entry["icon"] = icon
    if badge:
        entry["badge"] = badge
    if description:
        entry["description"] = description

    return entry


def enhance_frontmatter_for_nuxt(frontmatter: Dict[str, Any], page_type: str = "doc") -> Dict[str, Any]:
    """
    Enhance frontmatter with Nuxt Content specific fields.

    Args:
        frontmatter: Base frontmatter dictionary
        page_type: Type of page (doc, guide, reference, example)

    Returns:
        Enhanced frontmatter dictionary
    """
    enhanced = frontmatter.copy()

    # Add common Nuxt Content fields
    if "layout" not in enhanced:
        if page_type == "reference":
            enhanced["layout"] = "docs"
        else:
            enhanced["layout"] = "default"

    if "navigation" not in enhanced:
        enhanced["navigation"] = True

    # Add page type specific enhancements
    if page_type == "reference":
        enhanced.setdefault("aside", True)
        enhanced.setdefault("toc", True)
    elif page_type == "guide":
        enhanced.setdefault("aside", True)
        enhanced.setdefault("prev", True)
        enhanced.setdefault("next", True)
    elif page_type == "example":
        enhanced.setdefault("prose", True)
        enhanced.setdefault("copy", True)

    return enhanced


def generate_api_breadcrumbs(module_path: str, base_url: str = "/docs") -> List[Dict[str, str]]:
    """
    Generate breadcrumb navigation for API documentation.

    Args:
        module_path: Full module path (e.g., "mypackage.core.DataProcessor")
        base_url: Base URL for the documentation

    Returns:
        List of breadcrumb items
    """
    breadcrumbs = []

    parts = module_path.split(".")
    current_path = base_url

    for i, part in enumerate(parts):
        current_path += f"/{part}"

        if i == len(parts) - 1:
            # Last item (current page) - no link
            breadcrumbs.append({"title": part})
        else:
            breadcrumbs.append({"title": part, "to": current_path})

    return breadcrumbs


def format_python_signature_for_mdc(signature: str) -> str:
    """
    Format a Python function signature for better display in MDC.

    Args:
        signature: Python function signature string

    Returns:
        Formatted signature with syntax highlighting
    """
    # Simple formatting - could be enhanced with more sophisticated parsing
    formatted = signature.replace("(", "(\n  ").replace(", ", ",\n  ").replace(")", "\n)")

    return f"```python\n{formatted}\n```"


def create_api_overview_table(classes: List[Dict[str, str]]) -> str:
    """
    Create a table overview of API classes.

    Args:
        classes: List of dicts with 'name', 'description', and optional 'link' keys

    Returns:
        Markdown table string
    """
    if not classes:
        return ""

    table: str = "| Class | Description |\n"
    table += "|-------|-------------|\n"

    for cls in classes:
        name: str = cls.get("name", "")
        description: str = cls.get("description", "")
        link: str | None = cls.get("link")

        if link:
            name = f"[{name}]({link})"

        table += f"| {name} | {description} |\n"

    return table


class NuxtContentHelper:
    """
    Helper class for generating Nuxt Content compatible documentation.
    """

    def __init__(self, base_url: str = "/docs", use_mdc: bool = True, mdc_components: Optional[Dict[str, str]] = None):
        self.base_url = base_url
        self.use_mdc = use_mdc
        # Default to Nuxt UI components
        self.mdc_components = mdc_components or {
            "alert": "UAlert",
            "code_group": "UCodeGroup",
            "tabs": "UTabs",
            "variables": "UVariables",
            "arguments": "UArguments",
            "button": "UButton",
            "card": "UCard",
            "hero": "UPageHero",
            "feature": "ULandingCard",
        }

    def get_component_name(self, component_type: str) -> str:
        """Get the configured component name for a component type."""
        component = self.mdc_components.get(component_type, component_type)
        # Convert component name to kebab-case following MDC conventions
        return _convert_to_kebab_case(component)

    def wrap_with_mdc_if_enabled(self, content: str, component_type: str, props: str = "") -> str:
        """Wrap content with MDC component if MDC is enabled."""
        if self.use_mdc:
            component_name = self.get_component_name(component_type)
            return f"::{component_name}{{{props}}}\n{content}\n::"
        return content

    def create_hero_section(self, title: str, description: str, links: Optional[List[Dict[str, str]]] = None) -> str:
        """Create a hero section for documentation pages."""
        content = f"# {title}\n\n{description}\n"

        if links:
            content += "\n"
            for link in links:
                label = link.get("label", "Link")
                url = link.get("url", "#")
                variant = link.get("variant", "primary")

                if self.use_mdc:
                    button_component = self.get_component_name("button")
                    content += f'::{button_component}[{label}]{{to="{url}" variant="{variant}"}}\n'
                else:
                    content += f"[{label}]({url})\n"

        if self.use_mdc:
            hero_component = self.get_component_name("hero")
            return f"::{hero_component}\n{content}\n::"
        return content

    def create_feature_list(self, features: List[Dict[str, str]]) -> str:
        """Create a feature list section."""
        if not features:
            return ""

        content = ""
        for feature in features:
            title = feature.get("title", "")
            description = feature.get("description", "")
            icon = feature.get("icon", "")

            if self.use_mdc:
                feature_component = self.get_component_name("feature")
                icon_prop = f' icon="{icon}"' if icon else ""
                content += f'::{feature_component}{{title="{title}"{icon_prop}}}\n{description}\n::\n\n'
            else:
                content += f"### {title}\n\n{description}\n\n"

        return content.strip()

    def create_variables_section(self, variables: List[Dict[str, str]]) -> str:
        """Create a variables section using configured component."""
        if not variables:
            return ""

        if self.use_mdc:
            component = self.mdc_components.get("variables", "UVariables")
            return create_mdc_variables(variables, component)
        else:
            # Fallback to regular markdown table
            content: str = "## Variables\n\n"
            content += "| Name | Type | Description |\n"
            content += "|------|------|-------------|\n"
            for var in variables:
                name = var.get("name", "")
                type_info = var.get("type", "")
                description = var.get("content", "")
                content += f"| {name} | {type_info} | {description} |\n"
            return content

    def create_arguments_section(self, arguments: List[Dict[str, str]]) -> str:
        """Create an arguments section using configured component."""
        if not arguments:
            return ""

        if self.use_mdc:
            component = self.mdc_components.get("arguments", "UArguments")
            return create_mdc_arguments(arguments, component)
        else:
            # Fallback to regular markdown table
            content: str = "## Arguments\n\n"
            content += "| Name | Type | Description |\n"
            content += "|------|------|-------------|\n"
            for arg in arguments:
                name: str = arg.get("name", "")
                type_info: str = arg.get("type", "")
                description: str = arg.get("content", "")
                content += f"| {name} | {type_info} | {description} |\n"
            return content
