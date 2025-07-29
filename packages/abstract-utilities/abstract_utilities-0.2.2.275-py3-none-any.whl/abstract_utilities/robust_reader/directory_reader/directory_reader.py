import os
from typing import *
from ..file_filtering import is_allowed
from ..file_handlers import *
# ─── Example walker ──────────────────────────────────────────────────────────

def collect_files(
    root_dir: str,
    *,
    allowed: callable = is_allowed
) -> List[str]:
    """
    Walk `root_dir` recursively, returning a flat list of all files
    for which `allowed(path) is True`.
    """
    out = []
    for dirpath, dirnames, filenames in os.walk(root_dir):
        # mutate dirnames in-place to skip unwanted dirs
        dirnames[:] = [d for d in dirnames if d not in DEFAULT_EXCLUDE_DIRS]
        for fn in filenames:
            full = os.path.join(dirpath, fn)
            if allowed(full):
                out.append(full)
    return out

def read_directory(
    root_path: str,
) -> Dict[str, Union[pd.DataFrame, str]]:
    """
    Walk `root_path`, collect only files for which `is_allowed(path)` returns True.
    Returns a dict mapping relative path → either:
      • str (raw text)
      • pd.DataFrame or gpd.GeoDataFrame
      • for multi-sheet files, entries under "relpath::[sheetname]"
    """
    if not os.path.isdir(root_path):
        raise FileNotFoundError(f"Not a valid directory: {root_path!r}")

    root_path = os.path.abspath(root_path)
    root_prefix_len = len(root_path.rstrip(os.sep)) + 1

    collected: Dict[str, Union[pd.DataFrame, str]] = {}

    for full_path in collect_files(root_path):
        rel_path = full_path[root_prefix_len:]
        ext = Path(full_path).suffix.lower()

        # ——— 1) Pure-text quick reads —————————————
        if ext in {'.txt', '.md', '.csv', '.tsv', '.log'}:
            try:
                with open(full_path, 'r', encoding='utf-8', errors='replace') as f:
                    collected[rel_path] = f.read()
                _logger.info(f"Read text file: {rel_path}")
            except Exception as e:
                _logger.warning(f"Failed to read {rel_path} as text: {e}")
            continue

        # ——— 2) Try your DataFrame loader ——————————
        try:
            df_or_map = get_df(full_path)
            if isinstance(df_or_map, (pd.DataFrame, gpd.GeoDataFrame)):
                collected[rel_path] = df_or_map
                _logger.info(f"Loaded DataFrame: {rel_path}")
                continue

            if isinstance(df_or_map, dict):
                for sheet, df in df_or_map.items():
                    key = f"{rel_path}::[{sheet}]"
                    collected[key] = df
                    _logger.info(f"Loaded sheet DataFrame: {key}")
                continue
        except Exception as e:
            _logger.debug(f"get_df failed for {rel_path}: {e}")

        # ——— 3) Fallback to generic text extractor ————
        try:
            parts = read_file_as_text(full_path)  # List[str]
            combined = "\n\n".join(parts)
            collected[rel_path] = combined
            _logger.info(f"Read fallback text for: {rel_path}")
        except Exception as e:
            _logger.warning(f"Could not read {rel_path} at all: {e}")

    return collected
