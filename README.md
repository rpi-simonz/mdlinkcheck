# mdlinkcheck.py

Simple link checker for project-internal Markdown links.

Links to external targets are not checked. There are other tools for that.
But they can be listed with option `--show-external-links`.

Usually Markdown files in the current directory and subdirectories are checked.

If a directory (or more) are given as arguments that ones are checked instead.

## Installation

Simply copy the script into one of your PATH's directories and make it executable.



## Usage for project 'raspiBackupDoc'

Option `--raspiBackupDoc` enables the handling of the following asymmetry in [that project](https://github.com/framps/raspiBackupDoc):

The source files are in a **symmetric** directory structure:

    de/src/
    en/src/

but the generated HTML structure is **asymmetric**:
English as root and other language(s) as subdirectories:

    <files in English>
    ...
    de/<files in German>
