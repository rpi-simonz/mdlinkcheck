#!/usr/bin/env python
""" Simple link checker for project-internal Markdown links

Links to external targets are not checked but can be listed with option '-e'.
"""

import re
import sys
from pathlib import Path


SRCDIR = "de/src"


def check_anchor_in_target_file(target: Path,
                                anchor, is_local_anchor,
                                file: Path, line_number) -> None:
    """ Check if given anchor is in target file

     - as an html anchor "<a name="...">
     - as Markdown heading "# ..."
    """
    content = target.read_text()

    m1 = re.search(f'<a name="{anchor}">', content)
    m2 = re.search(f'# {anchor}', content, re.IGNORECASE)

    if m1 or m2:
        return

    if is_local_anchor:
        print(f"{file.as_posix()}:{line_number}:"
              f" Anchor not found: '{anchor}'")
    else:
        print(f"{file.as_posix()}:{line_number}:"
              f" Anchor not found"
              f" in target file '{target.as_posix()}':"
              f" '{anchor}'")


def has_external_link(target_filename,
                      file: Path, line_number,
                      show_external_links=False) -> bool:
    """ Check for and optionally report extern links """

    if not re.match(r"https*://", target_filename):
        return False

    if show_external_links:
        print(f"{file.as_posix()}:{line_number}:"
              f" Not checking external link:",
              target_filename)
    return True


def check_markdown_file(root: Path, file: Path, show_external_links) -> None:
    """ Check Markdown file for broken project-internal links """
    with file.open() as f:
        lines = f.readlines()

    for line_number, line in enumerate(lines, start=1):
        line = line.strip()
        m = re.search(r"\[.*?\]\((.*?)\)", line)
        if not m:
            continue

        target_filename = m.groups()[0]

        if has_external_link(target_filename, file, line_number,
                             show_external_links):
            continue

        try:
            target_filename, anchor = target_filename.split("#")
        except ValueError:
            anchor = ""

        if target_filename == "":   # the current file itself
            is_local_anchor = True
            target = file
        else:
            is_local_anchor = False
            target = root / target_filename

        if not target.exists():
            print(f"{file.as_posix()}:{line_number}:"
                  f" Target file not found: '{target.as_posix()}'")
            continue

        if anchor:
            check_anchor_in_target_file(target,
                                        anchor, is_local_anchor,
                                        file, line_number)


def walk_dir(directory: Path, show_external_links) -> None:
    """ Traverse given directory and check Markdown files """
    for root, _, files in Path(directory).walk(on_error=print):
        for file in files:
            file = root / file
            if file.suffix not in (".md", ".mkd", ".markdown"):
                continue
            check_markdown_file(root, file, show_external_links)


if __name__ == "__main__":

    SHOW_EXTERNAL_LINKS = False
    if len(sys.argv) > 1 and sys.argv[1] == "-e":
        SHOW_EXTERNAL_LINKS = True

    print("")
    print("*** Check project-internal links ***")
    walk_dir(SRCDIR, show_external_links=SHOW_EXTERNAL_LINKS)
    print("")
