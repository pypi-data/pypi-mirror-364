# file_reader.py

import os,glob
import fnmatch
from pathlib import Path
from typing import List, Optional, Set

from abstract_utilities import make_list,get_media_exts, is_media_type
def get_allowed(allowed=None):
    if allowed != False:
        if allowed == True:
            allowed = None
        allowed = allowed or make_allowed_predicate()
    else:
        def allowed(*args):
            return True
        allowed = allowed
    return allowed
def get_globs(items):
    glob_paths = []
    for item in make_list(items):
        pattern = os.path.join(item, "**/*")  # include all files recursively\n
        glob_paths += glob.glob(pattern, recursive=True)
    return glob_paths
def get_files(items,allowed=True):
    allowed = get_allowed(allowed=allowed)
    return [item for item in items if item and os.path.isfile(item) and allowed(item)]
def get_dirs(items,allowed=False):
    allowed = get_allowed(allowed=allowed)
    return [item for item in items if item and os.path.isdir(item) and allowed(item)]
def filter_files(items,allowed=None,files = []):
    allowed = get_allowed(allowed=allowed)
    glob_paths = get_globs(items)
    return [glob_path for glob_path in glob_paths if glob_path and os.path.isfile(glob_path) and glob_path not in files and allowed(glob_path)]
def filter_dirs(items,allowed=None,dirs = []):
    allowed = get_allowed(allowed=allowed)
    glob_paths = get_globs(items)
    return [glob_path for glob_path in glob_paths if glob_path and os.path.isdir(glob_path) and glob_path not in dirs and allowed(glob_path)]
def get_all_files(items,allowed=None):
    dirs = get_all_dirs(items)
    files = get_files(items)
    nu_files = []
    for directory in dirs:
        files += filter_files(directory,allowed=allowed,files=files)
    return files
def get_all_dirs(items,allowed=None):
    allowed = get_allowed(allowed=allowed)
    dirs = get_dirs(items)
    nu_dirs=[]
    for directory in dirs:
        nu_dirs += filter_dirs(directory,allowed=allowed,dirs=nu_dirs)
    return nu_dirs
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
_unallowed = set(get_media_exts(DEFAULT_EXCLUDE_TYPES)) | {'.shp', '.cpg', '.dbf', '.shx','.geojson',".pyc",'.shx','.geojson','.prj','.sbn','.sbx'}
DEFAULT_UNALLOWED_EXTS = {e for e in _unallowed if e not in DEFAULT_ALLOWED_EXTS}

DEFAULT_EXCLUDE_DIRS: Set[str] = {
    "node_modules", "__pycache__", "backups", "backup"
}

DEFAULT_EXCLUDE_PATTERNS: Set[str] = {
    "__init__*", "*.tmp", "*.log", "*.lock", "*.zip","*~"
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
    allowed_exts   = set(exclude_types or DEFAULT_ALLOWED_EXTS)
    unallowed_exts = set(unallowed_exts or DEFAULT_UNALLOWED_EXTS)
    exclude_types  = set(exclude_types or DEFAULT_EXCLUDE_TYPES)

    dirs_to_skip     = set(extra_dirs) | DEFAULT_EXCLUDE_DIRS
    patterns_to_skip = set(extra_patterns) |  DEFAULT_EXCLUDE_PATTERNS

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
                #input(name)
                return False

        # C) skip by media category
        if  p.is_file():
            ext = p.suffix.lower()
  

            if ext not in allowed_exts and ext in unallowed_exts:
                #print(ext)
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
        allowed_exts   = allowed_exts,
        unallowed_exts = unallowed_exts,
        exclude_types  = exclude_types,
        extra_dirs     = exclude_dirs,
        extra_patterns = exclude_file_patterns
    )
    roots = make_list(roots or [])
    original_dirs = get_dirs(roots,allowed=False)
    original_globs = get_globs(original_dirs)
    original_files = get_files(original_globs,allowed=False)
    original_exts = set(f".{file.split('.')[-1]}" for file in original_files if '.' in file)
    files=get_files(original_files,allowed=allowed)
    filtered_dirs = filter_dirs(original_dirs,allowed=allowed)
    for filtered_directory in filtered_dirs:
        files += filter_files(filtered_directory,allowed=allowed,files = files)
    
    return files
