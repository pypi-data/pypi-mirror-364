# file_reader.py

import os
import fnmatch
from pathlib import Path
from typing import List, Optional, Set

from abstract_utilities import make_list,get_media_exts, is_media_type

# ─── your global defaults ────────────────────────────────────────────────────

DEFAULT_ALLOWED_EXTS: Set[str] = {
    ".py", ".pyw",                             # python
    ".js", ".jsx", ".ts", ".tsx", ".mjs",      # JS/TS
    ".html", ".htm", ".xml",                   # markup
    ".css", ".scss", ".sass", ".less",         # styles
    ".json", ".yaml", ".yml", ".toml", ".ini",  # configs
    ".cfg", ".md", ".markdown", ".rst",        # docs
    ".sh", ".bash", ".env",                    # scripts/env
    ".txt"                                     # plain text
}

DEFAULT_EXCLUDE_TYPES: Set[str] = {
    "image", "video", "audio", "presentation",
    "spreadsheet", "archive", "executable"
}

# never want these—even if they sneak into ALLOWED
_unallowed = set(get_media_exts(DEFAULT_EXCLUDE_TYPES)) | {".pyc"}
DEFAULT_UNALLOWED_EXTS = {e for e in _unallowed if e not in DEFAULT_ALLOWED_EXTS}

DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules", "__pycache__", "backups", "backup"
}

DEFAULT_EXCLUDE_PATTERNS: Set[str] = {
    "__init__*", "*.tmp", "*.log", "*.lock", "*.zip"
}


# ─── 1) Build a predicate from user + defaults ──────────────────────────────

def make_allowed_predicate(
    *,
    allowed_exts:     Optional[Set[str]] = None,
    unallowed_exts:   Optional[Set[str]] = None,
    exclude_types:    Optional[Set[str]] = None,
    extra_dirs:       Optional[List[str]]  = None,
    extra_patterns:   Optional[List[str]]  = None,
) -> callable:
    allowed_exts   = allowed_exts   or DEFAULT_ALLOWED_EXTS
    unallowed_exts = unallowed_exts or DEFAULT_UNALLOWED_EXTS
    exclude_types  = exclude_types  or DEFAULT_EXCLUDE_TYPES

    dirs_to_skip     = set(extra_dirs or [])        | DEFAULT_EXCLUDE_DIRS
    patterns_to_skip = set(extra_patterns or [])    | DEFAULT_EXCLUDE_PATTERNS

    def allowed(path: str) -> bool:
        p    = Path(path)
        name = p.name.lower()

        # A) skip directories by name
        if p.is_dir() and name in dirs_to_skip:
            #input('is_dir dirs_to_skip')
            return False

        # B) skip by filename pattern
        for pat in patterns_to_skip:
            if fnmatch.fnmatch(name, pat.lower()):
                #input('fnmatch')
                return False

        # C) skip by media category
        
        if is_media_type(path, exclude_types):
            #input('is_media_type')
            return False

        # D) skip by extension
        ext = p.suffix.lower()
        if ext in unallowed_exts:
            #input('unallowed_exts')
            return False


        return True

    return allowed


# ─── 2) Walk & collect only “allowed” files ──────────────────────────────────

# in your file_reader.py
def collect_filepaths(
    roots: List[str],
    *,
    allowed_exts:     Set[str]=None,
    unallowed_exts:   Set[str]=None,
    exclude_types:    Set[str]=None,
    exclude_dirs:     List[str]=None,
    exclude_file_patterns: List[str]=None,
) -> List[str]:
    allowed = make_allowed_predicate(
        allowed_exts   = allowed_exts or DEFAULT_ALLOWED_EXTS,
        unallowed_exts = unallowed_exts or DEFAULT_UNALLOWED_EXTS,
        exclude_types  = exclude_types or DEFAULT_EXCLUDE_TYPES,
        extra_dirs     = exclude_dirs or DEFAULT_EXCLUDE_DIRS,
        extra_patterns = exclude_file_patterns or DEFAULT_EXCLUDE_PATTERNS
    )
    out = []
    for root in make_list(roots):
        for dirpath, dirnames, filenames in os.walk(root):
            dirnames[:] = [d for d in dirnames
                           if allowed(os.path.join(dirpath, d))]
            for fn in filenames:
                full = os.path.join(dirpath, fn)
                if allowed(full):
                    out.append(full)
    return out
