import os
from typing import *
from ..file_filtering import *
from ..file_handlers import *
# ─── Example walker ──────────────────────────────────────────────────────────
_logger = get_logFile(__name__)


def read_directory(
    root_path: str,
    *,
    allowed_exts:     Set[str] = DEFAULT_ALLOWED_EXTS,
    unallowed_exts:   Set[str] = DEFAULT_UNALLOWED_EXTS,
    exclude_types:    Set[str] = DEFAULT_EXCLUDE_TYPES,
    exclude_dirs:     List[str] = DEFAULT_EXCLUDE_DIRS,
    exclude_patterns: List[str] = DEFAULT_EXCLUDE_PATTERNS,
) -> Dict[str, Union[pd.DataFrame, str]]:

    
    collected = {}
    for root in make_list(root_path):
        root = os.path.abspath(root_path)
        prefix_len = len(root.rstrip(os.sep)) + 1
        for full in collect_files(
            root,
            allowed_exts     = allowed_exts,
            unallowed_exts   = unallowed_exts,
            exclude_types    = exclude_types,
            exclude_dirs     = exclude_dirs,
            exclude_patterns = exclude_patterns,
        ):
            rel = full[prefix_len:]
            ext = Path(full).suffix.lower()

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
