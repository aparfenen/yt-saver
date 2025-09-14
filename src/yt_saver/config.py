import os, sys, yaml
from __future__ import annotations
from dataclasses import dataclass
from importlib.resources import files
from typing import Dict, Any, Optional


@dataclass
class Config:
    raw: Dict[str, Any]

    @staticmethod
    def load(user_cfg: Optional[str]) -> "Config":
        # load defaults from package
        defaults = yaml.safe_load(files("yt_saver").joinpath("defaults.yaml").read_text())

        user = {}
        if user_cfg:
            with open(user_cfg, "r", encoding="utf-8") as f:
                user = yaml.safe_load(f) or {}

        # deep-merge (user overrides defaults)
        merged = _deep_merge(defaults, user)
        return Config(merged)

    def build_yt_dlp_opts(self, profile: str, save_dir: Optional[str], outtmpl_override: Optional[str]) -> Dict[str, Any]:
        d = self.raw
        prof = (d.get("profiles", {}) or {}).get(profile, {})

        # Base yt-dlp options
        opts: Dict[str, Any] = {}

        # Save paths
        base_dir = save_dir or d.get("save_dir") or "."
        os.makedirs(base_dir, exist_ok=True)
        opts["paths"] = {"home": base_dir}

        # Filename template
        outtmpl = outtmpl_override or d.get("outtmpl")
        if outtmpl:
            opts["outtmpl"] = os.path.join(base_dir, outtmpl)

        # Profile keys (format/container)
        for k in ("format", "merge_output_format", "remuxvideo"):
            v = prof.get(k)
            if v:
                opts[k] = v

        # Behavior flags
        for k, v in (d.get("behavior") or {}).items():
            if k == "download_archive":
                # put archive alongside downloads
                v = os.path.join(base_dir, v)
            opts[k] = v

        # Network
        for k, v in (d.get("network") or {}).items():
            opts[k] = v

        # Media
        for k, v in (d.get("media") or {}).items():
            opts[k] = v

        return opts

def _deep_merge(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = dict(a)
    for k, v in (b or {}).items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out
