from os import PathLike
from google_ai_studio_utils.config import google_ai_studio_html_template


def parse_csv_to_conversation(file_path: PathLike) -> list[tuple[str, str]]:
    # role, message tuples
    import sys
    import csv

    csv.field_size_limit(sys.maxsize)
    with open(file_path, "r") as file:
        reader = csv.reader(file)
        # next(reader)  # Skip the header
        conversation = [(row[0].replace(":", ""), row[1]) for row in reader]
    return conversation


def extract_chat_history_from_exported_python_code(
    python_code: str,
) -> list[tuple[str, str]]:
    import ast
    import re

    # def extract_history(source_code):
    module = ast.parse(python_code)
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "chat_session":
                    if isinstance(node.value, ast.Call):
                        for keyword in node.value.keywords:
                            if keyword.arg == "history":
                                for i, el in enumerate(keyword.value.elts):
                                    if isinstance(el, ast.Dict):
                                        for k, v in enumerate(el.values):
                                            if (
                                                isinstance(v, ast.Call)
                                                and v.func.id == "extract_pdf_pages"
                                            ):
                                                keyword.value.elts[i].values[k] = (
                                                    ast.List(
                                                        elts=[
                                                            ast.Str("File(s) attached")
                                                        ],
                                                        ctx=ast.Load(),
                                                    )
                                                )
                                            elif isinstance(v, ast.List) and isinstance(
                                                v.elts[0], ast.Subscript
                                            ):
                                                # print(v.elts)
                                                # print(
                                                #     f"v.value.elts[k].id: {v.value.elts[k].id}"
                                                # )
                                                keyword.value.elts[i].values[k] = (
                                                    ast.List(
                                                        elts=[
                                                            ast.Str("File(s) attached")
                                                        ],
                                                        ctx=ast.Load(),
                                                    )
                                                )
                                history = ast.literal_eval(keyword.value)
                                # def extract_pdf_pages(*args, **kwargs):
                                #     return ["Files attached"]
                                #
                                # history = ast.literal_eval(keyword.value)
                                # print(keyword.value)
                                # print(repr(keyword.value))
                                # modified_value = re.sub(
                                #     r"extract_pdf_pages(.+)",
                                #     "['File(s) attached']",
                                #     keyword.value,
                                # )
                                # history = ast.literal_eval(modified_value)

                                def extract_role_and_parts(history):
                                    return [
                                        (elem["role"], elem["parts"][0])
                                        for elem in history
                                        if "parts" in elem and len(elem["parts"]) > 0
                                    ]

                                return extract_role_and_parts(history)

    raise ValueError("No chat history found in the source code.")


# # Test the function
# python_code = """
# # convo = model.start_chat(history=[
# #   {
# #     "role": "user",
# #     "parts": ["鲁迅为什么暴打周树人？"]
# #   },
# #   {
# #     "role": "model",
# #     "parts": ["😅 哈哈，这真是个有趣的玩笑！鲁迅和周树人其实是一个人哦。鲁迅是周树人的笔名，他是一位著名的中国作家、思想家和革命家。"]
# #   },
# # ])
# # """
# print(extract_history(source_code))


def format_dunder_keys(s: str, **kwargs):
    for k, v in kwargs.items():
        k_ = f"__{k}__"
        s = s.replace(k_, v)
    return s


def conversation_to_html(
    conversation: list[tuple[str, str]],
    font: str = "sans-serif",
    title: str = "Google AI Studio Exported Conversation",
    no_thoughts: bool = False,
    expand_thoughts: bool = False,
) -> str:
    import markdown
    import html

    html_template = google_ai_studio_html_template.read_text()

    def separate_thoughts_from_content(message: str) -> tuple[str, str]:
        """Separate thoughts (marked with **headers** or standalone thought patterns) from regular content."""
        # Split the message into paragraphs
        paragraphs = message.split("\n\n")

        thoughts_paragraphs = []
        regular_paragraphs = []

        # Common thought patterns (case-insensitive)
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

        for paragraph in paragraphs:
            paragraph_lower = paragraph.strip().lower()
            is_thought = False

            # Check if paragraph starts with **header**
            if paragraph.strip().startswith("**") and "**" in paragraph[2:]:
                is_thought = True
            else:
                # Check for thought indicators
                for indicator in thought_indicators:
                    if indicator in paragraph_lower:
                        is_thought = True
                        break

                # Check if it's a standalone thought paragraph (starts with a capital letter and has introspective language)
                if not is_thought and paragraph.strip():
                    first_sentence = paragraph.strip().split(".")[0].lower()
                    if any(
                        word in first_sentence
                        for word in ["i've", "i'm", "my", "the initial", "further"]
                    ):
                        is_thought = True

            if is_thought:
                thoughts_paragraphs.append(paragraph)
            else:
                # Only add to regular content if it's not empty and not just whitespace
                if paragraph.strip():
                    regular_paragraphs.append(paragraph)

        thoughts = "\n\n".join(thoughts_paragraphs)
        regular_content = "\n\n".join(regular_paragraphs)

        return thoughts, regular_content

    def create_collapsible_thoughts(
        thoughts: str, index: int, expanded: bool = False
    ) -> str:
        """Create HTML for collapsible thoughts section."""
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
        expand_class = "expanded" if expanded else ""
        expand_attr = "open" if expanded else ""

        return f"""
        <div class="thoughts-container {expand_class}">
            <details {expand_attr} class="thoughts-details">
                <summary class="thoughts-summary">
                    <i class="fas fa-brain"></i> Model Thoughts
                    <i class="fas fa-chevron-down toggle-icon"></i>
                </summary>
                <div class="thoughts-content">
                    {thoughts_html}
                </div>
            </details>
        </div>
        """

    content = ""
    for index, (role, message) in enumerate(conversation):
        html_escaped_message = html.escape(message)
        if role.lower() == "model":
            thoughts, regular_content = separate_thoughts_from_content(message)

            # Build the model response HTML
            model_html = f'<a id="convo-item-{index}" class="anchor-button" href="#convo-item-{index}"># </a>'
            model_html += (
                f'<div class="model-content" data-message="{html_escaped_message}">'
            )

            # Add thoughts section if not hidden and thoughts exist
            if not no_thoughts and thoughts:
                model_html += create_collapsible_thoughts(
                    thoughts, index, expand_thoughts
                )

            # Add regular content if it exists
            if regular_content.strip():
                regular_html = markdown.markdown(
                    regular_content,
                    extensions=[
                        "footnotes",
                        "meta",
                        "toc",
                        "admonition",
                        "fenced_code",
                        "tables",
                    ],
                )
                model_html += f'<div class="regular-content">{regular_html}</div>'

            model_html += "</div><hr>"
            content += model_html
        else:
            # user input (plain text)
            content += f'<a id="convo-item-{index}" class="anchor-button" href="#convo-item-{index}"># </a><div class="user-content" data-message="{html_escaped_message}"><pre>{message}</pre></div><hr>'

    return format_dunder_keys(html_template, content=content, font=font, title=title)


def gist_create(p: PathLike) -> str:
    import subprocess

    # gh gist create p
    return subprocess.run(
        ["gh", "gist", "create", str(p)], capture_output=True, text=True
    ).stdout.strip()


def gist_url_to_gtm(gist_url: str, strip_tddschn: bool = True) -> str:
    to_replace = "https://gist.github.com/"
    if strip_tddschn and (to_replace + "tddschn/") in gist_url:
        to_replace += "tddschn/"
    url = gist_url.replace(to_replace, "https://g.teddysc.me/")
    return url


def github_copilot_json_conversation_to_html(
    json_data: dict,
    font: str = "sans-serif",
    title: str = "GitHub Copilot Chat Conversation",
) -> str:
    import markdown
    import html

    html_template = google_ai_studio_html_template.read_text()

    content = ""
    for index, request in enumerate(json_data["requests"]):
        role = "User" if request["message"]["kind"] == "text" else "Model"
        message = request["message"]["text"]
        html_escaped_message = html.escape(message)
        if role.lower() == "model":
            content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="model-content" data-message="{html_escaped_message}">{markdown.markdown(message, extensions=["footnotes", "meta", "toc", "admonition", "fenced_code", "tables"])}</div><hr>'
        else:
            content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="user-content" data-message="{html_escaped_message}"><pre>{message}</pre></div><hr>'

    return format_dunder_keys(html_template, content=content, font=font, title=title)


def github_copilot_json_conversation_to_html(
    json_data: dict,
    font: str = "sans-serif",
    title: str = "GitHub Copilot Chat Conversation",
) -> str:
    import markdown
    import html

    html_template = google_ai_studio_html_template.read_text()

    content = ""
    for index, request in enumerate(json_data["requests"]):
        role = "User" if request["message"]["kind"] == "text" else "Model"
        message = request["message"]["text"]
        html_escaped_message = html.escape(message)
        if role.lower() == "model":
            content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="model-content" data-message="{html_escaped_message}">{markdown.markdown(message, extensions=["footnotes", "meta", "toc", "admonition", "fenced_code", "tables"])}</div><hr>'
        else:
            content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="user-content" data-message="{html_escaped_message}"><pre>{message}</pre></div><hr>'

    return format_dunder_keys(html_template, content=content, font=font, title=title)


def github_copilot_json_conversation_to_html(
    json_data: dict,
    font: str = "sans-serif",
    title: str = "GitHub Copilot Chat Conversation",
) -> str:
    import markdown
    import html

    html_template = google_ai_studio_html_template.read_text()

    content = ""
    for index, request in enumerate(json_data["requests"]):
        message_parts = request["message"]["parts"]
        for part in message_parts:
            if "kind" in part and part["kind"] == "text":
                role = "User"
                message = part["text"]
            else:
                role = "Model"
                message = request["message"]["text"]
            html_escaped_message = html.escape(message)
            if role.lower() == "model":
                content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="model-content" data-message="{html_escaped_message}">{markdown.markdown(message, extensions=["footnotes", "meta", "toc", "admonition", "fenced_code", "tables"])}</div><hr>'
            else:
                content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="user-content" data-message="{html_escaped_message}"><pre>{message}</pre></div><hr>'

    return format_dunder_keys(html_template, content=content, font=font, title=title)


def github_copilot_json_conversation_to_html(
    json_data: dict,
    font: str = "sans-serif",
    title: str = "GitHub Copilot Chat Conversation",
) -> str:
    import markdown
    import html

    html_template = google_ai_studio_html_template.read_text()

    content = ""
    for index, request in enumerate(json_data["requests"]):
        message_parts = request["message"]["parts"]
        for part in message_parts:
            if "kind" in part and part["kind"] == "text":
                role = "User"
                message = part["text"]
                html_escaped_message = html.escape(message)
                content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="user-content" data-message="{html_escaped_message}"><pre>{message}</pre></div><hr>'
            else:
                role = "Model"
                message = request["message"]["text"]
                html_escaped_message = html.escape(message)
                content += f'<a id="convo-item-{index}"  class="anchor-button" href="#convo-item-{index}"># </a><div class="model-content" data-message="{html_escaped_message}">{markdown.markdown(message, extensions=["footnotes", "meta", "toc", "admonition", "fenced_code", "tables"])}</div><hr>'

    return format_dunder_keys(html_template, content=content, font=font, title=title)


def extract_google_ai_studio_conversation_from_python_code(
    python_code: str, include_base64: bool = False
) -> list[tuple[str, str]]:
    """Extract conversation from Google AI Studio generated Python code."""
    import ast

    def find_contents_assignment(node):
        """Recursively search for 'contents' assignment in AST nodes."""
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "contents":
                    if isinstance(node.value, ast.List):
                        conversation = []
                        for item in node.value.elts:
                            if isinstance(item, ast.Call):
                                # Extract role and parts from types.Content()
                                role = None
                                parts_text = ""

                                for keyword in item.keywords:
                                    if keyword.arg == "role":
                                        if isinstance(keyword.value, ast.Constant):
                                            role = keyword.value.value
                                    elif keyword.arg == "parts":
                                        # Extract text from parts
                                        if isinstance(keyword.value, ast.List):
                                            for part in keyword.value.elts:
                                                if isinstance(part, ast.Call):
                                                    # Look for text content in the arguments
                                                    if hasattr(part, "keywords"):
                                                        for kw in part.keywords:
                                                            if (
                                                                kw.arg == "text"
                                                                and isinstance(
                                                                    kw.value,
                                                                    ast.Constant,
                                                                )
                                                            ):
                                                                if isinstance(
                                                                    kw.value.value, str
                                                                ):
                                                                    parts_text += (
                                                                        kw.value.value
                                                                    )
                                                    # Also check positional arguments for from_text
                                                    if (
                                                        hasattr(part, "args")
                                                        and part.args
                                                    ):
                                                        for arg in part.args:
                                                            if isinstance(
                                                                arg, ast.Constant
                                                            ) and isinstance(
                                                                arg.value, str
                                                            ):
                                                                parts_text += arg.value
                                                    # If it's from_bytes, handle base64 content
                                                    if (
                                                        hasattr(part, "func")
                                                        and hasattr(part.func, "attr")
                                                        and getattr(
                                                            part.func, "attr", None
                                                        )
                                                        == "from_bytes"
                                                    ):
                                                        if include_base64:
                                                            # Try to extract base64 data and mime_type
                                                            mime_type = "application/octet-stream"
                                                            base64_data = ""

                                                            # Look for mime_type and data in keywords
                                                            if hasattr(
                                                                part, "keywords"
                                                            ):
                                                                for kw in part.keywords:
                                                                    if (
                                                                        kw.arg
                                                                        == "mime_type"
                                                                        and isinstance(
                                                                            kw.value,
                                                                            ast.Constant,
                                                                        )
                                                                    ):
                                                                        mime_type = kw.value.value
                                                                    elif (
                                                                        kw.arg == "data"
                                                                        and isinstance(
                                                                            kw.value,
                                                                            ast.Call,
                                                                        )
                                                                    ):
                                                                        # Extract base64.b64decode() argument
                                                                        if (
                                                                            hasattr(
                                                                                kw.value,
                                                                                "args",
                                                                            )
                                                                            and kw.value.args
                                                                            and isinstance(
                                                                                kw.value.args[
                                                                                    0
                                                                                ],
                                                                                ast.Constant,
                                                                            )
                                                                        ):
                                                                            base64_data = kw.value.args[
                                                                                0
                                                                            ].value

                                                            if (
                                                                base64_data
                                                                and isinstance(
                                                                    mime_type, str
                                                                )
                                                                and mime_type.startswith(
                                                                    "image/"
                                                                )
                                                            ):
                                                                # Embed image as data URL with zoom capability
                                                                parts_text += f'<img src="data:{mime_type};base64,{base64_data}" style="max-width: 100%; max-height: 800px; height: auto; cursor: zoom-in;" class="zoomable-image" />'
                                                            elif base64_data:
                                                                # Show as downloadable link for non-images
                                                                parts_text += f'<a href="data:{mime_type};base64,{base64_data}" download>📎 {mime_type} file</a>'
                                                            else:
                                                                parts_text += "[Binary data/Image]"
                                                        else:
                                                            if not parts_text:  # Only add if no text already found
                                                                parts_text += "[Binary data/Image]"

                                if role and parts_text:
                                    # Skip INSERT_INPUT_HERE placeholders
                                    if parts_text.strip() == "INSERT_INPUT_HERE":
                                        continue
                                    conversation.append((role, parts_text))

                        if conversation:
                            # Filter out trailing INSERT_INPUT_HERE entries
                            while (
                                conversation
                                and conversation[-1][1].strip() == "INSERT_INPUT_HERE"
                            ):
                                conversation.pop()
                            return conversation

        # Recursively search in child nodes
        for child in ast.iter_child_nodes(node):
            result = find_contents_assignment(child)
            if result:
                return result

        return None

    try:
        module = ast.parse(python_code)

        # Search through all nodes (including inside functions)
        for node in module.body:
            result = find_contents_assignment(node)
            if result:
                return result

    except SyntaxError:
        pass

    raise ValueError("No Google AI Studio conversation found in the source code.")
