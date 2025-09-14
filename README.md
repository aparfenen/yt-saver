# yt-saver
## ✦ Description
**yt-saver** is a lightweight but opinionated wrapper around yt-dlp.  

It was born out of frustration with messy filenames, scattered subtitle files, and 429 rate-limits.  
Instead of memorizing 20 flags, you just run:
`ytsave https://youtu.be/abc123` …and get a clean, consistent, archival-ready video in one step.



## ✦ Highlights / selling points
✔ **Clean filenames** → 2025-09-14_12-30-00 - 01 - My Great Video.webm  
✔ **Embedded everything** → subtitles, thumbnail, metadata all inside the file (no clutter).  
✔ **Anti-429 safe mode** → polite request pacing, retry backoff, fragment skipping.  
✔ **Archive support** → never download the same video twice.  
  

## ✦ Profiles out of the box:
✔ **webm** → best quality (VP9/AV1 + Opus)  
✔ **mp4** → maximum compatibility (H.264 + AAC)  
✔ **Easy config** → defaults in YAML, overridable per project.  
✔ **Batch friendly** → pass a URL list file, use numbering placeholders.  

## ✦ Usage

git clone https://github.com/aparfenen/yt-saver.git
cd yt-saver
python -m venv .venv && source .venv/bin/activate
pip install -e .

ytsave --dry-run https://youtu.be/ujTCoH21GlA



