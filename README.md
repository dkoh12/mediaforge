# mediaforge

A general-purpose media downloader built on [yt-dlp](https://github.com/yt-dlp/yt-dlp) and ffmpeg. Download audio and video from YouTube, SoundCloud, Vimeo, and 1000+ other sites.

## Features

- Download audio as MP3, M4A, WAV, FLAC, or Opus
- Download video as MP4, WebM, or MKV
- Choose audio quality (128 / 192 / 320 kbps)
- Simple CLI and browser-based GUI
- Works with any site supported by yt-dlp

## Requirements

- Python 3.9+
- ffmpeg (`sudo apt install ffmpeg` or `brew install ffmpeg`)
- yt-dlp (installed automatically via pip)

## Installation

```bash
pip install -e .
```

## CLI Usage

```bash
# Download audio (default: mp3, 192kbps)
mediaforge audio "https://youtube.com/watch?v=..."

# Download audio with options
mediaforge audio "https://soundcloud.com/..." --format flac --quality 320

# Download video (default: mp4)
mediaforge video "https://youtube.com/watch?v=..."

# Download video in webm
mediaforge video "https://vimeo.com/..." --format webm

# Launch the web GUI
mediaforge gui
```

## GUI

Open your browser at `http://localhost:5000` after running `mediaforge gui`. Paste a URL, pick your format and quality, and download.

## Supported Formats

| Type  | Formats                     |
|-------|-----------------------------|
| Audio | mp3, m4a, wav, flac, opus   |
| Video | mp4, webm, mkv              |

## Running Tests

```bash
pip install pytest
pytest tests/
```
