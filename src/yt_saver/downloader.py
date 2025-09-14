from __future__ import annotations
from typing import Iterable, Tuple, Dict, Any
from yt_dlp import YoutubeDL
import os

def _pjoin(*parts: str) -> str:
    """
    OS-safe join for outtmpl paths that may contain yt-dlp placeholders.
    We normalize to forward slashes so yt-dlp treats it consistently on all OSes.
    """
    cleaned = [p for p in parts if p]
    if not cleaned:
        return ""
    return os.path.join(*cleaned).replace("\\", "/")

def download_batch(
    videos: Iterable[Tuple[str, str]],  # [(idx, url), ...]
    base_opts: Dict[str, Any],
    filename_tpl: str | None = None,
    subdirs: Dict[str, str] | None = None,
) -> None:
    """
    For single videos:
      <save_dir>/<per_item>/<filename_tpl>

    For playlists:
      <save_dir>/<per_playlist>/<per_item>/<filename_tpl>

    Notes:
    - We probe metadata first (download=False) to decide whether the URL is a playlist.
    - If it *is* a playlist, we forcibly enable playlist processing (override --no-playlist).
    - {idx} in filename_tpl is replaced with the enumerated index from CLI, while
      per-item numbering inside a playlist can still rely on %(autonumber) or %(playlist_index).
    """
    subdirs = subdirs or {}
    per_item = subdirs.get("per_item", "%(title).80s [%(id)s]")
    per_playlist = subdirs.get("per_playlist", "%(playlist_title).80s [%(playlist_id)s]")

    base_dir = (base_opts.get("paths") or {}).get("home") or "."

    # Reuse a single YDL instance for the metadata probe
    probe_opts = dict(base_opts)
    with YoutubeDL(probe_opts) as ydl:
        for idx, url in videos:
            opts = dict(base_opts)

            # Probe to detect playlist vs single video; fall back to single on probe errors
            try:
                info = ydl.extract_info(url, download=False)
                is_playlist = (info.get("_type") == "playlist")
            except Exception:
                is_playlist = False

            # Build directory template
            if is_playlist:
                # Important: allow full playlist download (override --no-playlist)
                opts["noplaylist"] = False
                root = _pjoin(base_dir, per_playlist, per_item)
            else:
                root = _pjoin(base_dir, per_item)

            # Final filename template (inject {idx} if provided)
            item_filename = (filename_tpl or "%(upload_date>%Y-%m-%d)s - %(title).100s.%(ext)s").replace("{idx}", str(idx))

            # Compose final outtmpl (directories + file template)
            opts["outtmpl"] = _pjoin(root, item_filename)

            # Execute download with per-item template
            with YoutubeDL(opts) as dly:
                dly.download([url])
