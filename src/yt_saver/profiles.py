from __future__ import annotations
from typing import Dict, Any

def apply_profile(opts: Dict[str, Any], profile: str) -> Dict[str, Any]:
    # Translate YAML profile keys to yt-dlp keys
    p = {}
    if "format" in opts:            # if already set, respect CLI override
        p["format"] = opts["format"]
    return p  # real merge happens in config layer; kept minimal here
