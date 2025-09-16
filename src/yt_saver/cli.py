from __future__ import annotations
import argparse, sys
from pathlib import Path
from typing import Dict, Any, List
from yt_saver.config import Config
from yt_saver.downloader import download_batch


def parse_args():
    p = argparse.ArgumentParser(
        prog="ytsave",
        description="Opinionated yt-dlp wrapper (clean names, subs, metadata, anti-429, archives)."
    )
    p.add_argument("urls", nargs="*", help="Video URLs. If empty, provide --urls-file.")
    p.add_argument("--urls-file", "-U", help="Path to a text file with one URL per line.")
    p.add_argument("--config", "-c", help="Path to YAML config to override defaults.")
    p.add_argument("--profile", "-p", choices=["webm", "mp4", "mkv"], default="webm", help="Download profile.")
    p.add_argument("--save-dir", "-P", help="Output directory (overrides config).")
    p.add_argument("--template", "-t",
                   help="Filename template relative to save-dir. Use {idx} for numbering. Default: from config.")
    p.add_argument("--start-index", type=int, default=1, help="Starting index for {idx}.")
    # Subdir controls
    p.add_argument("--per-item-subdir", help="Subdir template for each video (yt-dlp placeholders). Overrides config.")
    p.add_argument("--per-playlist-subdir", help="Subdir template for playlist root (yt-dlp placeholders). Overrides config.")
    # Auth / network helpers
    p.add_argument("--cookies-from-browser", dest="cookies_from_browser",
                   help="BROWSER[:PROFILE], e.g. 'chrome' or 'chrome:Profile 1'")
    p.add_argument("--cookies", help="Path to cookies.txt (Netscape format)")
    p.add_argument("--impersonate", choices=["chrome", "chrome_120", "edge", "firefox", "safari"],
                   help="TLS/JA3 fingerprint to mimic a real browser")
    # YouTube playlist authcheck bypass
    p.add_argument("--yt-skip-authcheck", action="store_true",
                   help="For YouTube playlists: set extractor_args to youtubetab:skip=authcheck")
    p.add_argument("--dry-run", action="store_true", help="Show resolved yt-dlp opts and exit.")
    return p.parse_args()


def _merge_extractor_args(dst: Dict[str, Any] | None,
                          src: Dict[str, Dict[str, List[str]]]) -> Dict[str, Any]:
    out: Dict[str, Any] = {}
    if dst:
        for k, v in dst.items():
            out[k] = {ak: list(av) for ak, av in (v or {}).items()}
    for extr, args in src.items():
        cur = out.setdefault(extr, {})
        for key, vals in args.items():
            cur_list = cur.setdefault(key, [])
            for v in vals:
                if v not in cur_list:
                    cur_list.append(v)
    return out


def main():
    args = parse_args()
    cfg = Config.load(args.config)
    opts = cfg.build_yt_dlp_opts(profile=args.profile, save_dir=args.save_dir, outtmpl_override=None)
    subdirs = cfg.subdir_templates()

    if args.per_item_subdir:
        subdirs["per_item"] = args.per_item_subdir
    if args.per_playlist_subdir:
        subdirs["per_playlist"] = args.per_playlist_subdir

    if args.cookies_from_browser:
        if ":" in args.cookies_from_browser:
            b, prof = args.cookies_from_browser.split(":", 1)
            opts["cookiesfrombrowser"] = (b, prof)
        else:
            opts["cookiesfrombrowser"] = (args.cookies_from_browser, None)
    if args.cookies:
        opts["cookiefile"] = args.cookies
    if args.impersonate:
        opts["impersonate"] = args.impersonate

    # youtubetab authcheck skip (по требованию yt-dlp)
    if args.yt_skip_authcheck:
        skip_dict = {"youtubetab": {"skip": ["authcheck"]}}
        opts["extractor_args"] = _merge_extractor_args(opts.get("extractor_args"), skip_dict)

    urls = list(args.urls)
    if args.urls_file:
        urls += [ln.strip() for ln in Path(args.urls_file).read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not urls:
        print("No URLs provided. Use positional URLs or --urls-file.", file=sys.stderr)
        sys.exit(2)

    if args.dry_run:
        from pprint import pprint
        pprint(opts)
        print("Subdir templates:", subdirs)
        print(f"Sample outtmpl: {opts.get('outtmpl')}")
        sys.exit(0)

    vids = [(str(i), u) for i, u in enumerate(urls, start=args.start_index)]
    filename_tpl = args.template or "%(upload_date>%Y-%m-%d)s%(release_timestamp>_%H-%M-%S|)s - {idx} - %(title).100s.%(ext)s"
    download_batch(vids, opts, filename_tpl=filename_tpl, subdirs=subdirs)


if __name__ == "__main__":
    main()
