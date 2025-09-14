# 🎬 yt-dlp Cheat Sheet (yt-saver edition)

## 🗂️ Containers & Remux
| Option              | What it does | When to use | Container impact |
|---------------------|--------------|-------------|------------------|
| `merge_output_format` | Defines the final container format (mp4/webm/mkv) | To enforce a specific output format | Sets the extension of the result |
| `remuxvideo`        | Remux container without re-encoding | When streams don’t match the desired container | Fast, lossless, no quality change |
| `embedthumbnail`    | Embed cover art into video | Nice for media players | ⚠️ WebM → MKV (WebM cannot hold thumbnails) |
| `embedsubtitles`    | Embed subtitles into video | To avoid extra `.vtt/.srt` files | WebM supports only WebVTT; SRT → MKV |
| `addmetadata`       | Embed metadata (author, date, description) | To keep info inside the file | Usually no container change |

---

## 📂 Filenames
| Placeholder     | Example | Meaning |
|-----------------|---------|---------|
| `%(upload_date>%Y-%m-%d)s` | `2025-09-14` | Upload date |
| `%(release_timestamp>_%H-%M-%S|)s` | `_12-30-00` | Release time, if available |
| `%(autonumber)02d` | `01` | Autonumber in series |
| `%(title).100s` | `My Video Title` | First 100 chars of the title |
| `%(ext)s` | `.webm` | Container extension |

---

## 🌐 Network & Robustness
| Option | Meaning |
|--------|---------|
| `retries: 10` | Retry count for network errors |
| `fragment_retries: 10` | Retries for individual fragments |
| `retry_sleep: "http:exp=1:30,fragment:exp=1:20"` | Exponential backoff between retries |
| `concurrent_fragment_downloads: 3` | Download 3 fragments in parallel |
| `socket_timeout: 30` | Timeout for each request |
| `skip_unavailable_fragments: true` | Skip bad fragments instead of failing |
| `sleep_requests: 0.75` | Pause between requests (anti-429) |
| `max_sleep_interval: 20` | Random pauses up to 20s |

---

## ⚙️ Behavior
| Option | Meaning |
|--------|---------|
| `noplaylist: true` | Download only single video, not full playlist |
| `continuedl: true` | Resume broken downloads |
| `overwrites: false` | Do not overwrite existing files |
| `windowsfilenames: true` | Sanitize forbidden characters |
| `check_formats: true` | Ensure formats are actually downloadable |
| `download_archive: yt-dlp-archive.txt` | Keep history of downloaded IDs |
| `ignoreerrors: true` | Non-fatal errors continue |
| `no_abort_on_error: true` | Don’t stop on single video error |

---

## 🎙️ Subtitles & Metadata
| Option | What it does | Output |
|--------|--------------|--------|
| `writeinfojson: true` | Save metadata JSON | `*.info.json` |
| `writethumbnail: true` | Save thumbnail image | `*.jpg` or `*.webp` |
| `keep_thumbnail: false` | Delete after embedding | — |
| `writesubtitles: false` | Do not save external subs | — |
| `writeautomaticsub: true` | Enable auto-generated subtitles | embedded/temp |
| `keep_subtitles: false` | Remove `.vtt/.srt` after embedding | — |
| `subtitleslangs: ["en.*", "ru.*"]` | Languages to fetch | English + Russian |
| `subtitlesformat: "vtt/srt"` | Preferred subtitle formats | WebVTT or SRT |

---

## 🎥 Profiles
| Profile | Format | Use case |
|---------|--------|----------|
| **webm** | VP9/AV1 + Opus | Best quality, efficient compression |
| **mp4**  | H.264 + AAC | Compatibility with old devices |

---

## ⚡ Rules of Thumb
- **Rule 1:** If you embed thumbnails → expect **MKV**.  
- **Rule 2:** If you want strict `.webm`, set `embedthumbnail: false`.  
- **Rule 3:** Remux = safe, fast, no quality loss.  
