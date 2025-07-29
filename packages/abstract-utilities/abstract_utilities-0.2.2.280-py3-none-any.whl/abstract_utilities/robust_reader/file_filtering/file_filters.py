# file_reader.py

import os,fnmatch
from pathlib import Path
from typing import Set, List
from ...list_utils import make_list
from ...type_utils import get_media_exts, is_media_type  # assuming you have these

# ─── Configuration ────────────────────────────────────────────────────────────

# What you *do* want to include by extension:
DEFAULT_ALLOWED_EXTS: Set[str] = {
    # Python
    ".py", ".pyw",
    # JS / TS
    ".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs",
    # Markup
    ".html", ".htm", ".xml",
    # Styles
    ".css", ".scss", ".sass", ".less",
    # Data / config
    ".json", ".yaml", ".yml", ".toml", ".ini", ".cfg",
    # Docs
    ".md", ".markdown", ".rst",
    # Shell
    ".sh", ".bash",
    # Environment
    ".env",
    # Plain text
    ".txt",
}
DEFAULT_EXCLUDE_TYPES: Set[str] = {"image", "video", "audio", "presentation","spreadsheet","archive","executable"}
# What you *never* want, regardless
unallowed_exts: Set[str] = set(
    get_media_exts(DEFAULT_EXCLUDE_TYPES)
) | {".pyc"}

DEFAULT_UNALLOWED_EXTS: Set[str] = [unallowed_ext for unallowed_ext in list(unallowed_exts) if unallowed_ext not in list(DEFAULT_ALLOWED_EXTS)]
# Directory names to skip entirely
DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules",
    "__pycache__",
    "backups",
    "backup",
}

# Filename patterns to skip (uses fnmatch)
DEFAULT_EXCLUDE_PATTERNS: List[str] = [
    "__init__*",  # e.g. __init__.py or __init__.backup
    "*.tmp",
    "*.log",
    "*.lock",     # if you decide later you want lockfiles back you can remove this
    "*.zip",      # archives
]
def make_allowed_predicate(
    extra_dirs: List[str] = None,
    extra_file_patterns: List[str] = None
):
    """
    Returns an `allowed(path: str) -> bool` that merges
    DEFAULT_* with any extra_dirs or patterns the caller provided.
    """
    dirs_to_skip     = DEFAULT_EXCLUDE_DIRS.union(make_list(extra_dirs or []))
    patterns_to_skip = DEFAULT_EXCLUDE_PATTERNS.union(make_list(extra_file_patterns or []))

    def allowed(path: str) -> bool:
        p = Path(path)
        name = p.name.lower()

        # 1) skip directories by name
        if p.is_dir() and name in dirs_to_skip:
            return False

        # 2) skip by glob‐pattern
        for pat in patterns_to_skip:
            if fnmatch.fnmatch(name, pat.lower()):
                return False

        # 3) skip by media‐type category
        if is_media_type(path, DEFAULT_EXCLUDE_TYPES):
            return False

        # 4) extension based
        ext = p.suffix.lower()
        if ext in DEFAULT_UNALLOWED_EXTS:
            return False
        if ext not in DEFAULT_ALLOWED_EXTS:
            return False

        return True

    return allowed


# ─── Core predicate ───────────────────────────────────────────────────────────

def is_allowed(path: str) -> bool:
    """
    Return True if `path` should be included in our drop/concat step.
    Excludes:
      • Directories in DEFAULT_EXCLUDE_DIRS
      • Files matching DEFAULT_EXCLUDE_PATTERNS
      • Files whose extension is in DEFAULT_UNALLOWED_EXTS
      • Files whose media-type category is in DEFAULT_EXCLUDE_TYPES
      • Files *not* in DEFAULT_ALLOWED_EXTS
    """
    p = Path(path)
    name = p.name.lower()

    # 1) Skip dirs outright
    if p.is_dir() and name in DEFAULT_EXCLUDE_DIRS:
        return False

    # 2) Skip by glob-pattern
    for pat in DEFAULT_EXCLUDE_PATTERNS:
        if fnmatch.fnmatch(name, pat.lower()):
            return False

    # 3) Skip by media-type category (images, video, audio, presentation)
    #    Assumes your is_media_type(filename, media_types=...) helper
    if is_media_type(path, DEFAULT_EXCLUDE_TYPES):
        return False

    # 4) Extension checks
    ext = p.suffix.lower()
    if ext in DEFAULT_UNALLOWED_EXTS:
        return False
    if ext not in DEFAULT_ALLOWED_EXTS:
        return False

    # Passed all filters → keep it
    return True
def collect_files(
    root_dir: str,
    *,
    allowed: callable = is_allowed,
    exclude_dirs=None,
    exclude_file_patterns=None,
) -> List[str]:
    """
    Walk `root_dir` recursively, returning a flat list of all files
    for which `allowed(path) is True`.
    """
    allowed = make_allowed_predicate(
        extra_dirs=exclude_dirs,
        extra_file_patterns=exclude_file_patterns
    )
    out = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # mutate dirnames in-place to skip unwanted dirs
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if allowed(full):
                out.append(full)
    return out
