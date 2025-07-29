from __future__ import annotations

import os
import re
import tempfile
import zipfile

import requests

import fnmatch
import mimetypes
from collections import defaultdict
from typing import Iterable, List, Set, Sequence, Optional

import pathspec


GITHUB_ZIP_URL = "https://github.com/{owner}/{repo}/archive/refs/heads/{branch}.zip"
REPO_ID_REGEX = re.compile(
    r"""
    (?:git@github\.com:|https?://github\.com/)?
    (?P<owner>[^/]+)/
    (?P<repo>[^/]+?)(?:\.git)?$
    """,
    re.VERBOSE,
)


def parse_repo_id(repo_id: str) -> tuple[str, str]:
    """Extract owner and repo name from <owner>/<repo> or URL/SSH forms."""
    m = REPO_ID_REGEX.search(repo_id.strip())
    if not m:
        raise ValueError(f"Can't parse GitHub repo from '{repo_id}'")
    return m.group("owner"), m.group("repo")


def download_and_unpack(owner: str, repo: str, branch: str) -> tuple[str, str]:
    """Download the branch ZIP and unpack into a temp dir. Returns (path to root, branch)."""
    url = GITHUB_ZIP_URL.format(owner=owner, repo=repo, branch=branch)
    resp = requests.get(url, stream=True)
    resp.raise_for_status()

    td = tempfile.mkdtemp(prefix="github_to_md_")
    zip_path = os.path.join(td, "repo.zip")
    with open(zip_path, "wb") as f:
        for chunk in resp.iter_content(32_768):
            f.write(chunk)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(td)

    # Find the single subdirectory
    entries = [d for d in os.listdir(td) if os.path.isdir(os.path.join(td, d))]
    if len(entries) != 1:
        raise RuntimeError(f"Unexpected ZIP layout: {entries}")
    return os.path.join(td, entries[0]), branch


# Popular lock-files that should never be included in the Markdown output
_LOCK_FILE_NAMES: Set[str] = {
    # Node / JS
    "package-lock.json",
    "yarn.lock",
    "pnpm-lock.yaml",
    "npm-shrinkwrap.json",
    # Python
    "poetry.lock",
    "Pipfile.lock",
    "poetry.lock",
    "requirements.lock",
    "conda-lock.yml",
    "uv.lock",
    # Ruby / Bundler
    "Gemfile.lock",
    # Rust / Cargo
    "Cargo.lock",
    # Go
    "go.sum",
    # PHP / Composer
    "composer.lock",
    # Swift / CocoaPods
    "Podfile.lock",
    # JVM / Gradle & others
    "gradle.lockfile",
    "gradle-dependencies.lock",
    # Dart / Flutter
    "pubspec.lock",
    # Elixir
    "mix.lock",
    # Terraform
    "terraform.lock.hcl",
    # Haskell / Cabal
    "cabal.project.freeze",
    # Dotnet
    "packages.lock.json",
    # C# NuGet
    "project.assets.json",
    # Misc
    "vcpkg-lock.json",
}

# Common binary / non-text extensions we never want in the output
_BINARY_EXTS: Set[str] = {
    # Images
    ".png", ".jpg", ".jpeg", ".gif", ".bmp", ".tiff", ".tif", ".ico", ".icns", ".webp", ".svg",
    # Audio / video
    ".mp3", ".wav", ".flac", ".ogg", ".mp4", ".mkv", ".mov", ".avi", ".wmv", ".webm",
    # Archives / packages
    ".zip", ".tar", ".gz", ".tgz", ".bz2", ".xz", ".lz", ".7z", ".rar",
    # Fonts
    ".ttf", ".otf", ".woff", ".woff2",
    # Documents / misc binaries
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    # Compiled / generated artifacts
    ".class", ".jar", ".war", ".ear", ".dll", ".so", ".dylib", ".exe", ".obj", ".o", ".a", ".bin",
    ".pyc", ".pyo",
}


# ---------------------------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------------------------

def _is_binary_by_extension(path: str) -> bool:
    """Return True if the filename has a known binary extension."""
    _, ext = os.path.splitext(path)
    return ext.lower() in _BINARY_EXTS


def _is_binary_by_content(path: str, read_size: int = 1024) -> bool:
    """Detect binary files by reading the first *read_size* bytes."""
    try:
        with open(path, "rb") as fp:
            chunk = fp.read(read_size)
        if b"\0" in chunk:
            return True
        # Fallback: rely on mimetypes – treat text/ * as text
        mime, _ = mimetypes.guess_type(path)
        if mime and not mime.startswith("text"):
            # application/json is fine, treat as text
            if mime == "application/json":
                return False
            return True
        # Try decoding as UTF-8 – if fails it's likely binary
        try:
            chunk.decode("utf-8")
        except UnicodeDecodeError:
            return True
        return False
    except (FileNotFoundError, PermissionError, OSError):
        return True


def _is_text_file(path: str) -> bool:
    """Return True if *path* appears to be a text file."""
    return not _is_binary_by_extension(path) and not _is_binary_by_content(path)


def _load_gitignore_spec(repo_root: str) -> pathspec.PathSpec | None:
    """Load .gitignore from *repo_root* if present using gitwildmatch rules."""
    gitignore_path = os.path.join(repo_root, ".gitignore")
    if not os.path.exists(gitignore_path):
        return None

    with open(gitignore_path, "r", encoding="utf-8", errors="ignore") as fp:
        patterns = fp.readlines()
    return pathspec.PathSpec.from_lines("gitwildmatch", patterns)


# ---------------------------------------------------------------------------
# Tree builder
# ---------------------------------------------------------------------------

def _build_tree(repo_root: str, included_files: Iterable[str]) -> str:
    """Return a *tree(1)*-like directory layout based on *included_files*.

    *included_files* must be an iterable of paths relative to *repo_root* (using
    os.sep as separator).
    """
    # Build mapping of directory -> children names
    children: defaultdict[str, List[str]] = defaultdict(list)
    for rel_path in included_files:
        parts = rel_path.split(os.sep)
        for level in range(len(parts)):
            parent = os.sep.join(parts[:level])
            name = parts[level]
            if name not in children[parent]:
                children[parent].append(name)

    # Sort the children lists for deterministic output
    for key in children:
        children[key].sort()

    lines: List[str] = ["."]

    def _recurse(dir_key: str, prefix: str):
        entries = children.get(dir_key, [])
        for idx, name in enumerate(entries):
            is_last = idx == len(entries) - 1
            connector = "└── " if is_last else "├── "
            lines.append(f"{prefix}{connector}{name}")
            child_key = f"{dir_key}{os.sep}{name}" if dir_key else name
            if child_key in children:
                extension = "    " if is_last else "│   "
                _recurse(child_key, prefix + extension)

    _recurse("", "")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Core public API
# ---------------------------------------------------------------------------

def _split_filters(items: Optional[Sequence[str]]) -> list[str]:
    """Flatten a list of include/exclude CLI values (which may contain ';')
    
    Automatically strips './' prefix from patterns for convenience.
    """
    if not items:
        return []
    out: list[str] = []
    for item in items:
        if item is None:
            continue
        # Split on ';' but keep empty segments out
        segments = [seg.strip() for seg in item.split(";") if seg.strip()]
        # Strip './' prefix if present
        for seg in segments:
            if seg.startswith("./"):
                seg = seg[2:]
            out.append(seg)
    return out


def _matches_any(rel_path: str, patterns: list[str]) -> bool:
    """Return True if *rel_path* matches any of *patterns* using fnmatch/glob rules."""
    for pat in patterns:
        pat_clean = pat.rstrip("/")
        if fnmatch.fnmatch(rel_path, pat_clean):
            return True
        if rel_path.startswith(pat_clean + os.sep):
            return True
    return False


def repo_to_markdown(
    path: str,
    *,
    includes: Optional[Sequence[str]] = None,
    excludes: Optional[Sequence[str]] = None,
    branch: Optional[str] = None,
) -> str:
    """Return a Markdown string that combines a *tree* output and file contents.

    Args:
        path: Root of repository to process.
        includes: Optional list of include patterns (relative to *path*)
        excludes: Optional list of exclude patterns (relative to *path*)
        branch: Optional branch name for GitHub repos
    """
    path = os.path.abspath(os.path.expanduser(path))
    gitignore_spec = _load_gitignore_spec(path)

    include_patterns = _split_filters(includes)
    exclude_patterns = _split_filters(excludes)

    included_files: List[str] = []

    # Walk repository
    for root, dirs, files in os.walk(path):
        # Skip .git directory early
        if ".git" in dirs:
            dirs.remove(".git")
        rel_dir = os.path.relpath(root, path)
        rel_dir = "" if rel_dir == "." else rel_dir

        # Directory pruning when include patterns exist – best-effort optimisation
        if include_patterns and rel_dir:
            # if no include pattern overlaps this directory prefix, skip
            if not any(pat.startswith(rel_dir + os.sep) or rel_dir.startswith(pat.rstrip("/")) for pat in include_patterns):
                # continue walking; pruning is tricky, so we let loop continue without pruning dirs list for correctness
                pass

        for fname in files:
            rel_path = os.path.join(rel_dir, fname) if rel_dir else fname

            # Include / exclude filters
            if include_patterns:
                if not _matches_any(rel_path, include_patterns):
                    continue  # not in include list

            if exclude_patterns and _matches_any(rel_path, exclude_patterns):
                continue  # explicitly excluded

            # Ignore lock files
            if os.path.basename(fname) in _LOCK_FILE_NAMES:
                continue

            # Gitignore patterns
            if gitignore_spec and gitignore_spec.match_file(rel_path):
                continue

            abs_path = os.path.join(root, fname)

            # Skip non-text/binary
            if not _is_text_file(abs_path):
                continue

            included_files.append(rel_path)

    included_files.sort()

    tree_str = _build_tree(path, included_files)

    project_name = os.path.basename(path)
    parts: List[str] = []
    if branch:
        parts.append(f"### Repository {project_name} (branch: {branch})\n\n")
    else:
        parts.append(f"### Repository {project_name}\n\n")
    parts.append("### File tree:\n")
    parts.append(tree_str)

    # Append file contents
    for rel_path in included_files:
        abs_path = os.path.join(path, rel_path)
        parts.append("\n\n")
        parts.append(f"file: {rel_path}\n")
        parts.append(f"```{os.path.splitext(rel_path)[1].lstrip('.')}  # {rel_path}\n")
        try:
            with open(abs_path, "r", encoding="utf-8", errors="replace") as fp:
                parts.append(fp.read())
        except Exception as exc:  # pragma: no cover – unforeseen read errors
            parts.append(f"<error reading file: {exc}>")
        parts.append("\n```")

    parts.append("\n\n")
    return "".join(parts)
