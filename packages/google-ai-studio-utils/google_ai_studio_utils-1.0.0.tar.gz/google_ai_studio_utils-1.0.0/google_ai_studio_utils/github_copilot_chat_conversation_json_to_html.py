#!/usr/bin/env python3
"""
Author : GitHub Copilot
Date   : 2024-04-14
Purpose: Convert GitHub Copilot Chat JSON to HTML
"""

import argparse
import json
from pathlib import Path
from google_ai_studio_utils.utils import (
    github_copilot_json_conversation_to_html,
    gist_create,
    gist_url_to_gtm,
)


def get_args():
    """Get command-line arguments"""
    parser = argparse.ArgumentParser(
        description="Convert GitHub Copilot Chat JSON to HTML",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("path", metavar="path", type=Path, help="Path to JSON file")
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


def main():
    """Make a jazz noise here"""
    args = get_args()
    json_data = json.loads(args.path.read_text())

    kwargs = {}
    if args.title:
        kwargs["title"] = args.title
    elif not args.no_file_stem_as_title:
        kwargs["title"] = args.path.stem
    if args.font:
        kwargs["font"] = args.font

    html_content = github_copilot_json_conversation_to_html(json_data, **kwargs)
    args.save = args.save or args.publish or args.open

    if not args.save and not args.publish:
        print(html_content)
        return

    if args.save:
        import tempfile
        from pathlib import Path

        temp_dir = Path(tempfile.mkdtemp(prefix="gai_"))
        temp_file: Path = temp_dir / args.path.name
        temp_file = (
            temp_file.with_suffix(".html")
            if temp_file.suffix
            else temp_file.with_suffix(".html")
        )
        temp_file.write_text(html_content)
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
