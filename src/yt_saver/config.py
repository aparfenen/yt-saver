from __future__ import annotations
import os, yaml
from dataclasses import dataclass
from typing import Dict, Any, Optional
from importlib.resources import files

@dataclass
class Config:
    raw: Dict[str, Any]

    @staticmethod
    def load(user_cfg: Optional[str]) -> "Config":
        """
        Load package defaults (defaults.yaml) and deep-merge user overrides.
        """
        defaults = yaml.safe_load(files("yt_saver").joinpath("defaults.yaml").read_text())
        user = {}
        if user_cfg:
            with open(user_cfg, "r", encoding="utf-8") as f:
                user = yaml.safe_load(f) or {}
        merged = _deep_merge(defaults, user)
        return Config(merged)

    def build_yt_dlp_opts(self, profile: str, save_dir: Optional[str], outtmpl_override: Optional[str]) -> Dict[str, Any]:
        """
        Build a yt-dlp options dict from config + selected profile.
        Note: per-item/per-playlist subdirs are applied in downloader.py.
        """
        d = self.raw
        prof = (d.get("profiles", {}) or {}).get(profile, {})

        opts: Dict[str, Any] = {}

        # Base output directory
        base_dir = save_dir or d.get("save_dir") or "."
        os.makedirs(base_dir, exist_ok=True)
        opts["paths"] = {"home": base_dir}

        # Filename template (the *file* part; subdir templates are added later)
        outtmpl = outtmpl_override or d.get("outtmpl")
        if outtmpl:
            opts["outtmpl"] = os.path.join(base_dir, outtmpl)

        # Profile-level container/format preferences
        for k in ("format", "merge_output_format", "remuxvideo"):
            v = prof.get(k)
            if v is not None:
                opts[k] = v

        # Behavior flags (archive path is relative to base_dir)
        for k, v in (d.get("behavior") or {}).items():
            if k == "download_archive":
                v = os.path.join(base_dir, v)
            opts[k] = v

        # Network options
        for k, v in (d.get("network") or {}).items():
            opts[k] = v

        # Media options (subtitles/thumbnail/metadata)
        for k, v in (d.get("media") or {}).items():
            opts[k] = v

        # Advanced
        adv = d.get("advanced") or {}
        if adv.get("outtmpl_na_placeholder"):
            opts["outtmpl_na_placeholder"] = adv["outtmpl_na_placeholder"]

        return opts

    def subdir_templates(self) -> Dict[str, str]:
        """
        Return subdir templates used by downloader to build per-item/playlist dirs.
        """
        s = self.raw.get("subdirs") or {}
        return {
            "per_item": s.get("per_item", "%(title).80s [%(id)s]"),
            "per_playlist": s.get("per_playlist", "%(playlist_title).80s [%(playlist_id)s]"),
        }

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    """
    Recursively merge dict b into dict a (b overrides a).
    """
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out
