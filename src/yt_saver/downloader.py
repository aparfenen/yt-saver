import os
from __future__ import annotations
from typing import Iterable, Tuple, Dict, Any
from yt_dlp import YoutubeDL


def download_batch(
    videos: Iterable[Tuple[str, str]],  # [(idx, url), ...]
    base_opts: Dict[str, Any],
    filename_tpl: str | None = None,
) -> None:
    for idx, url in videos:
        opts = dict(base_opts)  # copy per item

        if filename_tpl:
            # ensure per-item template (with idx) overrides global outtmpl
            base_dir = opts.get("paths", {}).get("home", ".")
            opts["outtmpl"] = os.path.join(
                base_dir,
                filename_tpl.replace("{idx}", str(idx))
            )

        with YoutubeDL(opts) as ydl:
            ydl.download([url])
