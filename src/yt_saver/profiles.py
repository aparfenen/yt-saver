from __future__ import annotations
from typing import Dict, Any

def apply_profile(opts: Dict[str, Any], profile: str) -> Dict[str, Any]:
    """
    Kept for compatibility; real merging happens in Config.
    """
    return opts
