# google_ai_studio_utils/google_ai_studio_conversation_python_to_html.py
#!/usr/bin/env python3
"""
Author : GitHub Copilot
Date   : 2024-04-14
Purpose: Convert Google AI Studio conversation from Python code to HTML
"""

import argparse
from pathlib import Path
from google_ai_studio_utils.utils import (
    extract_google_ai_studio_conversation_from_python_code,
    conversation_to_html,
    gist_create,
    gist_url_to_gtm,
)
from google_ai_studio_utils.metadata_utils import (
    extract_metadata_from_python_code,
    format_metadata_as_html,
)


def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert Google AI Studio conversation from Python code to HTML",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "path",
        metavar="path",
        type=Path,
        help="Path to Python file containing Google AI Studio conversation",
    )
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
    parser.add_argument(
        "-b",
        "--include-base64-content",
        help="Include base64 content (images, files) instead of showing '[Binary data]'",
        action="store_true",
    )
    parser.add_argument(
        "-T",
        "--no-thoughts",
        help="Hide model thoughts (reasoning process) and show only the final output",
        action="store_true",
    )
    parser.add_argument(
        "--expand-thoughts",
        help="Expand all thoughts by default when HTML is opened",
        action="store_true",
    )
    return parser.parse_args()


def main():
    """Make a jazz noise here"""
    args = get_args()
    python_code = args.path.read_text()

    # Extract conversation and metadata
    conversation = extract_google_ai_studio_conversation_from_python_code(
        python_code, include_base64=args.include_base64_content
    )
    metadata = extract_metadata_from_python_code(python_code)
    metadata_html = format_metadata_as_html(metadata)

    # Prepare arguments for HTML generation
    kwargs = {}
    if args.title:
        kwargs["title"] = args.title
    elif not args.no_file_stem_as_title:
        kwargs["title"] = args.path.stem
    if args.font:
        kwargs["font"] = args.font

    kwargs["no_thoughts"] = args.no_thoughts
    kwargs["expand_thoughts"] = args.expand_thoughts
    kwargs["metadata_html"] = metadata_html  # Pass metadata HTML to the function

    # Generate HTML
    html_content = conversation_to_html(conversation, **kwargs)
    args.save = args.save or args.publish or args.open

    if not args.save and not args.publish:
        print(html_content)
        return

    if args.save or args.publish:
        import tempfile

        temp_dir = Path(tempfile.mkdtemp(prefix="gai_"))
        temp_file: Path = (temp_dir / args.path.name).with_suffix(".html")
        temp_file.write_text(html_content)
        if args.save:
            print(f"Saved to {temp_file}")
        if args.open and not args.publish:
            import webbrowser

            webbrowser.open(f"file://{temp_file}")
        if args.publish:
            gist_url = gist_create(temp_file)
            gtm_url = gist_url_to_gtm(gist_url)
            print(f"Created Gist at {gist_url}")
            print(f"Published to {gtm_url}")
            import pyperclip

            pyperclip.copy(gtm_url)
            if args.open:
                import webbrowser

                webbrowser.open(gtm_url)


if __name__ == "__main__":
    main()
