from __future__ import annotations
from typing import Iterable, Tuple, Dict, Any
from yt_dlp import YoutubeDL
import os


def _pjoin(*parts: str) -> str:
    """
    Join path segments for yt-dlp's outtmpl.
    Always normalize to forward slashes so yt-dlp treats it consistently across OSes.
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
    Output layout:

      Single video:
        <save_dir>/<per_item>/<filename_tpl>

      Playlist:
        <save_dir>/<per_playlist>/<per_item>/<filename_tpl>

    Notes:
    - We first probe metadata (download=False) to decide whether the URL is a playlist.
    - For playlists we forcibly enable playlist processing (override --no-playlist).
    - {idx} in filename_tpl:
        * single URL → replaced with the enumerated CLI index (1, 2, 3, ...)
        * playlist   → replaced with %(playlist_index)03d (001, 002, ...)
    - Per-item numbering inside a playlist can also rely on %(autonumber) if desired.
    """
    subdirs = subdirs or {}
    per_item = subdirs.get("per_item", "%(title).80s [%(id)s]")
    per_playlist = subdirs.get("per_playlist", "%(playlist_title).80s [%(playlist_id)s]")

    base_dir = (base_opts.get("paths") or {}).get("home") or "."

    # Quiet probe to avoid duplicate loud logs during metadata detection
    probe_opts = dict(base_opts)
    probe_opts.update({
        "quiet": True,
        "no_warnings": True,
        "verbose": False,
    })

    with YoutubeDL(probe_opts) as ydl_probe:
        for idx, url in videos:
            # Copy base opts for the actual download
            opts = dict(base_opts)

            # Detect playlist vs single video
            try:
                info = ydl_probe.extract_info(url, download=False)
                is_playlist = (info.get("_type") == "playlist")
            except Exception:
                # On probe errors assume single video to keep going
                is_playlist = False

            # Build directory template
            if is_playlist:
                # Important: allow full playlist download (override --no-playlist)
                opts["noplaylist"] = False
                root = _pjoin(base_dir, per_playlist, per_item)
            else:
                root = _pjoin(base_dir, per_item)

            # Choose filename template and inject index
            raw_tpl = filename_tpl or "%(upload_date>%Y-%m-%d)s - %(title).100s.%(ext)s"
            if is_playlist:
                # Per-item index inside the playlist (001, 002, ...)
                item_filename = raw_tpl.replace("{idx}", "%(playlist_index)03d")
            else:
                item_filename = raw_tpl.replace("{idx}", str(idx))

            # Compose final outtmpl (directories + file template)
            opts["outtmpl"] = _pjoin(root, item_filename)

            # Execute download with the per-item template
            with YoutubeDL(opts) as ydl:
                ydl.download([url])
