#!/usr/bin/env python
""" Simple link checker for project-internal Markdown links

Links to external targets are not checked. There are other tools for that.
But they can be listed with option `--show-external-links`.

Usually Markdown files in the current directory and subdirectories are checked.

If a directory (or more) are given as arguments that ones are checked instead.


## Installation

Simply copy the script into one of your PATH's directories
and make it executable.


---------------------------------------------------------------

## Usage for project 'raspiBackupDoc'

Option `--raspiBackupDoc` enables the handling of the following asymmetry
in that project (https://github.com/framps/raspiBackupDoc):

The source files are in a **symmetric** directory structure:

    de/src/
    en/src/

but the generated HTML structure is **asymmetric**:
English as root and other language(s) as subdirectories:

    <files in English>
    ...
    de/<files in German>

---------------------------------------------------------------
"""

import argparse
import re
from pathlib import Path


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


def check_markdown_file(root: Path, file: Path,
                        show_external_links=False,
                        raspibackupdoc=False) -> None:
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
            target = file
            is_local_anchor = True
        else:
            is_local_anchor = False

            if raspibackupdoc:
                # special handling for raspiBackupDoc
                if target_filename.startswith("../"):
                    target_filename = "../../en/src/" + target_filename[3:]
                elif target_filename.startswith("de/"):
                    target_filename = "../../de/src/" + target_filename[3:]
                # end special handling

            target = root / target_filename

        if not target.exists():
            print(f"{file.as_posix()}:{line_number}:"
                  f" Target file not found: '{target.as_posix()}'")
            continue

        if anchor:
            check_anchor_in_target_file(target,
                                        anchor, is_local_anchor,
                                        file, line_number)


def walk_dir(directory: Path,
             show_external_links=False,
             raspibackupdoc=False) -> None:
    """ Traverse given directory and check Markdown files """
    for root, _, files in Path(directory).walk(on_error=print):
        for file in files:
            file = root / file
            if file.suffix not in (".md", ".mkd", ".markdown"):
                continue
            check_markdown_file(root, file,
                                show_external_links=show_external_links,
                                raspibackupdoc=raspibackupdoc)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
                    prog='mdlinkcheck.py',
                    formatter_class=argparse.RawDescriptionHelpFormatter,
                    description=__doc__)

    parser.add_argument('pathes', nargs='*', default=["."], metavar='path')
    parser.add_argument('--raspiBackupDoc',
                        help='special handling regarding directory structure',
                        action='store_true')
    parser.add_argument('--show-external-links',
                        action='store_true')

    args = parser.parse_args()

    print("*** Check project-internal links ***\n")

    for srcdir in args.pathes:
        walk_dir(srcdir, show_external_links=args.show_external_links,
                 raspibackupdoc=args.raspiBackupDoc)
    print("")
