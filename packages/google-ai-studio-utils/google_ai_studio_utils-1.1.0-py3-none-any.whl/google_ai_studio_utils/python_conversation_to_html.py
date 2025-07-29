# google_ai_studio_utils/python_conversation_to_html.py
#!/usr/bin/env python3
"""
Author : GitHub Copilot
Date   : 2024-07-23
Purpose: Convert Python files with Google AI Studio conversation generation to HTML with metadata
"""
# THIS FILE IS KEPT FOR BACKWARDS COMPATIBILITY OR OTHER POTENTIAL USES
# The main entrypoint is now google_ai_studio_conversation_python_to_html.py

import argparse
from pathlib import Path
from google_ai_studio_utils.utils import (
    gist_create,
    gist_url_to_gtm,
    conversation_to_html,
)
from google_ai_studio_utils.metadata_utils import (
    extract_metadata_from_python_code,
    format_metadata_as_html,
)
from google_ai_studio_utils.utils import (
    extract_google_ai_studio_conversation_from_python_code,
)


def get_args():
    parser = argparse.ArgumentParser(
        description="Convert Python file with Google AI Studio conversation to HTML with metadata",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("path", metavar="path", type=Path, help="Path to Python file")
    parser.add_argument("-t", "--title", help="Title of the HTML page", metavar="title")
    parser.add_argument(
        "-f", "--font", help="Font-Family of the HTML page", metavar="font"
    )
    parser.add_argument(
        "-s", "--save", help="Save the HTML page to disk", action="store_true"
    )
    parser.add_argument(
        "-p",
        "--publish",
        help="Publish the HTML page to GitHub Gist",
        action="store_true",
    )
    parser.add_argument(
        "-o", "--open", help="Open the HTML page in browser", action="store_true"
    )
    parser.add_argument(
        "--no-file-stem-as-title",
        help="Do not use the file stem as title",
        action="store_true",
    )
    return parser.parse_args()


def python_conversation_to_html_with_metadata(python_code: str, **kwargs) -> str:
    metadata = extract_metadata_from_python_code(python_code)
    metadata_html = format_metadata_as_html(metadata)
    conversation = extract_google_ai_studio_conversation_from_python_code(python_code)
    kwargs["metadata_html"] = metadata_html
    return conversation_to_html(conversation, **kwargs)


def main():
    args = get_args()
    python_code = args.path.read_text()
    kwargs = {}
    if args.title:
        kwargs["title"] = args.title
    elif not args.no_file_stem_as_title:
        kwargs["title"] = args.path.stem
    if args.font:
        kwargs["font"] = args.font
    html_content = python_conversation_to_html_with_metadata(python_code, **kwargs)
    if args.save or args.publish or args.open:
        import tempfile

        temp_dir = Path(tempfile.mkdtemp(prefix="gai_"))
        temp_file = (temp_dir / args.path.name).with_suffix(".html")
        temp_file.write_text(html_content)
        if args.save:
            print(f"Saved to {temp_file}")
        # ... rest of save/publish logic ...
    else:
        print(html_content)


if __name__ == "__main__":
    main()
