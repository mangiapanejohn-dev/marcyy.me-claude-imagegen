"""Local storage for the imagegen skill's OpenAI API key and (optional)
custom API base URL, for third-party OpenAI-compatible relay/proxy services.

Not a CLI entrypoint — imported by image_gen.py and configure_key.py (both
live in this same directory, so Python's automatic script-dir sys.path entry
makes this importable without any packaging).
"""

# imagegen · by Marc (marcyy.me)

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_DIR = Path(os.environ.get("XDG_CONFIG_HOME", "~/.config")).expanduser() / "claude-imagegen"
CONFIG_FILE = CONFIG_DIR / "config.json"


def _load_raw() -> Dict[str, Any]:
    if not CONFIG_FILE.exists():
        return {}
    try:
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def load_key() -> Optional[str]:
    key = _load_raw().get("openai_api_key")
    return key.strip() if isinstance(key, str) and key.strip() else None


def load_base_url() -> Optional[str]:
    base_url = _load_raw().get("base_url")
    return base_url.strip() if isinstance(base_url, str) and base_url.strip() else None


def save_config(updates: Dict[str, Optional[str]]) -> None:
    """Merge `updates` into the stored config. A value of None deletes that field."""
    data = _load_raw()
    for field, value in updates.items():
        if value is None:
            data.pop(field, None)
        else:
            data[field] = value

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    os.chmod(CONFIG_DIR, 0o700)
    CONFIG_FILE.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.chmod(CONFIG_FILE, 0o600)


def save_key(key: str) -> None:
    save_config({"openai_api_key": key.strip()})


def delete_key() -> bool:
    if CONFIG_FILE.exists():
        CONFIG_FILE.unlink()
        return True
    return False


def status() -> dict:
    exists = CONFIG_FILE.exists()
    mode_ok: Optional[bool] = None
    if exists:
        mode_ok = (CONFIG_FILE.stat().st_mode & 0o777) == 0o600
    return {
        "configured": exists and load_key() is not None,
        "path": str(CONFIG_FILE),
        "mode_ok": mode_ok,
        "base_url": load_base_url(),
    }
