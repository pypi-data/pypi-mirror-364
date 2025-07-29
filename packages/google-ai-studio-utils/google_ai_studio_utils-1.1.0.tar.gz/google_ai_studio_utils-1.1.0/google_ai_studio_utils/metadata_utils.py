# google_ai_studio_utils/metadata_utils.py
"""Utilities for extracting and formatting metadata from Python code."""

import ast


def extract_metadata_from_python_code(python_code: str) -> dict:
    metadata = {}
    try:
        tree = ast.parse(python_code)
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "model":
                        if isinstance(node.value, ast.Constant):
                            metadata["model"] = node.value.value
                        elif hasattr(node.value, "s"):
                            metadata["model"] = getattr(node.value, "s")
            elif isinstance(node, ast.Call):
                for keyword in getattr(node, "keywords", []):
                    if keyword.arg == "googleSearch":
                        if "tools" not in metadata:
                            metadata["tools"] = []
                        metadata["tools"].append("Google Search")
                    elif keyword.arg == "thinking_budget":
                        if isinstance(keyword.value, ast.UnaryOp) and isinstance(
                            keyword.value.op, ast.USub
                        ):
                            if (
                                hasattr(keyword.value, "operand")
                                and isinstance(keyword.value.operand, ast.Constant)
                                and keyword.value.operand.value == 1
                            ):
                                metadata["thinking_budget"] = "unlimited"
                        elif isinstance(keyword.value, ast.Constant):
                            metadata["thinking_budget"] = keyword.value.value
                        elif hasattr(keyword.value, "n"):
                            metadata["thinking_budget"] = getattr(keyword.value, "n")
                    elif keyword.arg == "response_mime_type":
                        if isinstance(keyword.value, ast.Constant):
                            metadata["response_mime_type"] = keyword.value.value
                        elif hasattr(keyword.value, "s"):
                            metadata["response_mime_type"] = getattr(keyword.value, "s")
    except Exception:
        pass
    return metadata


def format_metadata_as_html(metadata: dict) -> str:
    if not metadata:
        return ""
    content_parts = []
    if "model" in metadata:
        content_parts.append(f"<strong>Model:</strong> {metadata['model']}")
    if "tools" in metadata:
        content_parts.append(f"<strong>Tools:</strong> {', '.join(metadata['tools'])}")
    if "thinking_budget" in metadata:
        budget = metadata["thinking_budget"]
        content_parts.append(
            f"<strong>Thinking Budget:</strong> {'Unlimited' if budget == 'unlimited' else budget}"
        )
    if "response_mime_type" in metadata:
        content_parts.append(
            f"<strong>Response MIME Type:</strong> {metadata['response_mime_type']}"
        )
    if not content_parts:
        return ""
    content_html = "<br>".join(content_parts)
    return f"""
    <details class="thoughts-details mb-4">
        <summary class="thoughts-summary">
            <i class="fas fa-cog"></i> Configuration Metadata <i class="fas fa-chevron-down toggle-icon"></i>
        </summary>
        <div class="thoughts-content"><div class="text-sm text-gray-700">{content_html}</div></div>
    </details>
    """
