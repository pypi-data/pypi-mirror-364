# google_ai_studio_utils/utils.py
from os import PathLike
from google_ai_studio_utils.config import google_ai_studio_html_template
import ast
import re
import markdown
import html


# --- Existing functions like parse_csv_to_conversation, etc. can stay if they exist ---
def parse_csv_to_conversation(file_path: PathLike) -> list[tuple[str, str]]:
    # ... implementation ...
    import sys
    import csv

    csv.field_size_limit(sys.maxsize)
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        conversation = [(row[0].replace(":", ""), row[1]) for row in reader]
    return conversation


def format_dunder_keys(s: str, **kwargs):
    for k, v in kwargs.items():
        k_ = f"__{k}__"
        s = s.replace(k_, v)
    return s


# --- THIS IS THE CORRECT, FULLY MERGED FUNCTION ---
def conversation_to_html(
    conversation: list[tuple[str, str]],
    font: str = "sans-serif",
    title: str = "Google AI Studio Exported Conversation",
    no_thoughts: bool = False,
    expand_thoughts: bool = False,
    metadata_html: str = "",  # <-- THE NEW ARGUMENT
) -> str:
    html_template = google_ai_studio_html_template.read_text()

    def separate_thoughts_from_content(message: str) -> tuple[str, str]:
        paragraphs = message.split("\n\n")
        thoughts_paragraphs, regular_paragraphs = [], []
        thought_indicators = [
            "examining the image",
            "pinpointing the artist",
            "identifying the object",
            "assessing material",
            "analyzing",
            "developing",
            "my initial focus",
            "now, i'm delving",
            "i've made headway",
            "i've acknowledged",
            "i understand",
            "i need to emphasize",
        ]
        for p in paragraphs:
            is_thought = False
            if p.strip().startswith("**") and "**" in p[2:]:
                is_thought = True
            else:
                for ind in thought_indicators:
                    if ind in p.strip().lower():
                        is_thought = True
                        break
                if (
                    not is_thought
                    and p.strip()
                    and any(
                        w in p.strip().split(".")[0].lower()
                        for w in ["i've", "i'm", "my", "the initial", "further"]
                    )
                ):
                    is_thought = True
            if is_thought:
                thoughts_paragraphs.append(p)
            elif p.strip():
                regular_paragraphs.append(p)
        return "\n\n".join(thoughts_paragraphs), "\n\n".join(regular_paragraphs)

    def create_collapsible_thoughts(thoughts: str, expanded: bool = False) -> str:
        if not thoughts.strip():
            return ""
        thoughts_html = markdown.markdown(
            thoughts,
            extensions=[
                "footnotes",
                "meta",
                "toc",
                "admonition",
                "fenced_code",
                "tables",
            ],
        )
        return f'<div class="thoughts-container {"expanded" if expanded else ""}"><details {"open" if expanded else ""} class="thoughts-details"><summary class="thoughts-summary"><i class="fas fa-brain"></i> Model Thoughts <i class="fas fa-chevron-down toggle-icon"></i></summary><div class="thoughts-content">{thoughts_html}</div></details></div>'

    content = metadata_html  # <-- METADATA IS ADDED HERE
    for index, (role, message) in enumerate(conversation):
        escaped_msg = html.escape(message)
        anchor = f'<a id="convo-item-{index}" class="anchor-button" href="#convo-item-{index}"># </a>'
        if role.lower() == "model":
            thoughts, regular_content = separate_thoughts_from_content(message)
            model_html = f'<div class="model-content" data-message="{escaped_msg}">'
            if not no_thoughts and thoughts:
                model_html += create_collapsible_thoughts(thoughts, expand_thoughts)
            if regular_content.strip():
                model_html += f'<div class="regular-content">{markdown.markdown(regular_content, extensions=["footnotes", "meta", "toc", "admonition", "fenced_code", "tables"])}</div>'
            model_html += "</div>"
            content += anchor + model_html + "<hr>"
        else:
            content += f'{anchor}<div class="user-content" data-message="{escaped_msg}"><pre>{message}</pre></div><hr>'

    return format_dunder_keys(html_template, content=content, font=font, title=title)


# --- THE REST OF THE UTILS FILE ---
def extract_google_ai_studio_conversation_from_python_code(
    python_code: str, include_base64: bool = False
) -> list[tuple[str, str]]:
    # ... (The full implementation of this function from your previous correct state)
    def find_contents_assignment(node):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "contents":
                    if isinstance(node.value, ast.List):
                        conversation = []
                        for item in node.value.elts:
                            if isinstance(item, ast.Call):
                                role, parts_text = None, ""
                                for keyword in item.keywords:
                                    if keyword.arg == "role" and isinstance(
                                        keyword.value, ast.Constant
                                    ):
                                        role = keyword.value.value
                                    elif keyword.arg == "parts" and isinstance(
                                        keyword.value, ast.List
                                    ):
                                        for part in keyword.value.elts:
                                            if isinstance(part, ast.Call):
                                                if hasattr(part, "keywords"):
                                                    for kw in part.keywords:
                                                        if (
                                                            kw.arg == "text"
                                                            and isinstance(
                                                                kw.value, ast.Constant
                                                            )
                                                            and isinstance(
                                                                kw.value.value, str
                                                            )
                                                        ):
                                                            parts_text += kw.value.value
                                                if hasattr(part, "args") and part.args:
                                                    for arg in part.args:
                                                        if isinstance(
                                                            arg, ast.Constant
                                                        ) and isinstance(
                                                            arg.value, str
                                                        ):
                                                            parts_text += arg.value
                                                if (
                                                    hasattr(part, "func")
                                                    and hasattr(part.func, "attr")
                                                    and getattr(part.func, "attr", None)
                                                    == "from_bytes"
                                                ):
                                                    if include_base64:
                                                        mime_type, base64_data = (
                                                            "application/octet-stream",
                                                            "",
                                                        )
                                                        if hasattr(part, "keywords"):
                                                            for kw in part.keywords:
                                                                if (
                                                                    kw.arg
                                                                    == "mime_type"
                                                                    and isinstance(
                                                                        kw.value,
                                                                        ast.Constant,
                                                                    )
                                                                ):
                                                                    mime_type = (
                                                                        kw.value.value
                                                                    )
                                                                elif (
                                                                    kw.arg == "data"
                                                                    and isinstance(
                                                                        kw.value,
                                                                        ast.Call,
                                                                    )
                                                                    and hasattr(
                                                                        kw.value, "args"
                                                                    )
                                                                    and kw.value.args
                                                                    and isinstance(
                                                                        kw.value.args[
                                                                            0
                                                                        ],
                                                                        ast.Constant,
                                                                    )
                                                                ):
                                                                    base64_data = (
                                                                        kw.value.args[
                                                                            0
                                                                        ].value
                                                                    )
                                                        if (
                                                            base64_data
                                                            and mime_type.startswith(
                                                                "image/"
                                                            )
                                                        ):
                                                            parts_text += f'<img src="data:{mime_type};base64,{base64_data}" style="max-width: 100%; max-height: 800px; height: auto; cursor: zoom-in;" class="zoomable-image" />'
                                                        elif base64_data:
                                                            parts_text += f'<a href="data:{mime_type};base64,{base64_data}" download>📎 {mime_type} file</a>'
                                                        else:
                                                            parts_text += (
                                                                "[Binary data/Image]"
                                                            )
                                                    else:
                                                        if not parts_text:
                                                            parts_text += (
                                                                "[Binary data/Image]"
                                                            )
                                if (
                                    role
                                    and parts_text
                                    and parts_text.strip() != "INSERT_INPUT_HERE"
                                ):
                                    conversation.append((role, parts_text))
                        if conversation:
                            while (
                                conversation
                                and conversation[-1][1].strip() == "INSERT_INPUT_HERE"
                            ):
                                conversation.pop()
                            return conversation
        for child in ast.iter_child_nodes(node):
            result = find_contents_assignment(child)
            if result:
                return result
        return None

    try:
        module = ast.parse(python_code)
        for node in module.body:
            result = find_contents_assignment(node)
            if result:
                return result
    except SyntaxError:
        pass
    raise ValueError("No Google AI Studio conversation found in the source code.")


def gist_create(p: PathLike) -> str:
    # ... implementation ...
    import subprocess

    return subprocess.run(
        ["gh", "gist", "create", str(p)], capture_output=True, text=True
    ).stdout.strip()


def gist_url_to_gtm(gist_url: str, strip_tddschn: bool = True) -> str:
    # ... implementation ...
    to_replace = "https://gist.github.com/"
    if strip_tddschn and (to_replace + "tddschn/") in gist_url:
        to_replace += "tddschn/"
    return gist_url.replace(to_replace, "https://g.teddysc.me/")


def github_copilot_json_conversation_to_html(
    json_data: dict,
    font: str = "sans-serif",
    title: str = "GitHub Copilot Chat Conversation",
) -> str:
    # ... implementation ...
    html_template = google_ai_studio_html_template.read_text()
    content = ""
    for index, request in enumerate(json_data["requests"]):
        message_parts = request["message"]["parts"]
        for part in message_parts:
            role = "User" if "kind" in part and part["kind"] == "text" else "Model"
            message = part.get("text") or request["message"].get("text", "")
            html_escaped_message = html.escape(message)
            if role.lower() == "model":
                content += f'<a id="convo-item-{index}" class="anchor-button" href="#convo-item-{index}"># </a><div class="model-content" data-message="{html_escaped_message}">{markdown.markdown(message, extensions=["footnotes", "meta", "toc", "admonition", "fenced_code", "tables"])}</div><hr>'
            else:
                content += f'<a id="convo-item-{index}" class="anchor-button" href="#convo-item-{index}"># </a><div class="user-content" data-message="{html_escaped_message}"><pre>{message}</pre></div><hr>'
    return format_dunder_keys(html_template, content=content, font=font, title=title)
