from __future__ import annotations
import argparse, sys
from pathlib import Path
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

    # Profiles
    p.add_argument("--profile", "-p", choices=["webm", "mp4", "mkv"], default="webm",
                   help="Download profile.")

    # Output / templating
    p.add_argument("--save-dir", "-P", help="Output directory (overrides config).")
    p.add_argument(
        "--template", "-t",
        help="Filename template relative to save-dir. Use {idx} for numbering. Default: from config."
    )
    p.add_argument("--start-index", type=int, default=1,
                   help="Starting index for {idx} when enumerating input URLs.")

    # Subdir controls (applied by wrapper; yt-dlp placeholders allowed)
    p.add_argument("--per-item-subdir",
                   help="Subdir template for each video (yt-dlp placeholders). Overrides config.")
    p.add_argument("--per-playlist-subdir",
                   help="Subdir template for playlist root (yt-dlp placeholders). Overrides config.")

    # Anti-429 / auth helpers (pass-through to yt-dlp)
    p.add_argument("--cookies-from-browser", dest="cookies_from_browser",
                   help="BROWSER[:PROFILE], e.g. 'chrome' or 'chrome:Profile 1'")
    p.add_argument("--cookies", help="Path to cookies.txt (Netscape format)")
    p.add_argument("--impersonate", choices=["chrome", "chrome_120", "edge", "firefox", "safari"],
                   help="TLS/JA3 fingerprint to mimic a real browser")

    # Introspection
    p.add_argument("--dry-run", action="store_true",
                   help="Show resolved yt-dlp opts and exit.")

    return p.parse_args()


def main():
    args = parse_args()
    cfg = Config.load(args.config)

    # Build base yt-dlp options from config/profile
    opts = cfg.build_yt_dlp_opts(
        profile=args.profile,
        save_dir=args.save_dir,
        outtmpl_override=None,
    )

    # Apply subdir templates (used by downloader to build per-item/per-playlist dirs)
    subdirs = cfg.subdir_templates()
    if args.per_item_subdir:
        subdirs["per_item"] = args.per_item_subdir
    if args.per_playlist_subdir:
        subdirs["per_playlist"] = args.per_playlist_subdir

    # Pass-through auth/anti-bot options to yt-dlp
    if args.cookies_from_browser:
        parts = args.cookies_from_browser.split(":", 1)
        opts["cookiesfrombrowser"] = tuple(parts) if len(parts) == 2 else (parts[0],)
    if args.cookies:
        opts["cookies"] = args.cookies
    if args.impersonate:
        opts["impersonate"] = args.impersonate

    # Collect URLs
    urls = list(args.urls)
    if args.urls_file:
        urls += [ln.strip() for ln in Path(args.urls_file).read_text(encoding="utf-8").splitlines() if ln.strip()]
    if not urls:
        print("No URLs provided. Use positional URLs or --urls-file.", file=sys.stderr)
        sys.exit(2)

    # Dry run shows the final yt-dlp opts (including cookies/impersonate) and templates
    if args.dry_run:
        from pprint import pprint
        pprint(opts)
        print("Subdir templates:", subdirs)
        print(f"Sample outtmpl: {opts.get('outtmpl')}")
        sys.exit(0)

    # Build iterable of (idx, url) for the downloader
    vids = [(str(i), u) for i, u in enumerate(urls, start=args.start_index)]

    # Per-item filename template (the file name part; subdirs applied in downloader)
    filename_tpl = args.template or "%(upload_date>%Y-%m-%d)s%(release_timestamp>_%H-%M-%S|)s - {idx} - %(title).100s.%(ext)s"

    # Execute batch download with structured subdirectories
    download_batch(vids, opts, filename_tpl=filename_tpl, subdirs=subdirs)


if __name__ == "__main__":
    main()
