import argparse
import sys
import os
import textwrap

from ._core import (
    download_and_unpack,
    parse_repo_id,
    repo_to_markdown,
)


def _determine_repo_dir(source: str, branch: str) -> tuple[str, str | None]:
    """Return a local directory for *source* which can be either a local
    filesystem path or a GitHub *owner/name* expression. In the latter case the
    repository is downloaded as a ZIP archive. If *source* is None or empty,
    defaults to current directory.
    
    Returns:
        tuple: (directory_path, branch_name_or_none)
    """
    expanded = os.path.expanduser(source)
    if os.path.exists(expanded):
        return os.path.abspath(expanded), None

    # Treat as GitHub repo ID
    owner, repo = parse_repo_id(source)
    return download_and_unpack(owner, repo, branch)


def run():
    p = argparse.ArgumentParser(
        prog="repo-to-md",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=textwrap.dedent(
            """
            Convert a GitHub repository (or a local path) into a single Markdown document
            containing a *tree* listing and concatenated source files.

            SOURCE can be one of the following (defaults to current directory):
              • <owner>/<repo>
              • https://github.com/<owner>/<repo>.git
              • git@github.com:<owner>/<repo>.git
              • /absolute/or/relative/path/to/local/dir
              • . (current directory, default)
            """
        ).strip(),
    )

    p.add_argument("source", nargs="?", default=".", help="GitHub repository or local filesystem path (default: current directory)")
    p.add_argument("-b", "--branch", default="main", help="GitHub branch to download (default: main)")
    p.add_argument("-o", "--output", metavar="FILE", help="Write Markdown to FILE instead of stdout")
    p.add_argument(
        "-i",
        "--include",
        metavar="PATTERN",
        action="append",
        help="Include pattern(s). May be used multiple times or separated with ';'. When supplied, only matching paths are considered for output.",
    )
    p.add_argument(
        "-e",
        "--exclude",
        metavar="PATTERN",
        action="append",
        help="Exclude pattern(s). May be used multiple times or separated with ';'. Applied after include filtering.",
    )

    args = p.parse_args()

    try:
        repo_dir, repo_branch = _determine_repo_dir(args.source, args.branch)
    except ValueError as exc:
        sys.exit(str(exc))

    markdown = repo_to_markdown(
        repo_dir,
        includes=args.include,
        excludes=args.exclude,
        branch=repo_branch,
    )

    if args.output:
        out_path = os.path.abspath(args.output)
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as fp:
            fp.write(markdown)
        print(f"Markdown written to {out_path}")
    else:
        sys.stdout.write(markdown)
