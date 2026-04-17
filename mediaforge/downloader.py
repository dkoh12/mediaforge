import yt_dlp
from pathlib import Path
from dataclasses import dataclass

AUDIO_QUALITIES = ("128", "192", "320")
AUDIO_FORMATS = ("mp3", "m4a", "wav", "flac", "opus")
VIDEO_FORMATS = ("mp4", "webm", "mkv")


@dataclass
class MediaInfo:
    title: str
    uploader: str
    duration: int   # seconds
    url: str


def get_info(url: str) -> MediaInfo:
    """Fetch metadata for a URL without downloading."""
    opts = {"quiet": True, "no_warnings": True, "skip_download": True}
    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=False)
    return MediaInfo(
        title=info.get("title", "Unknown"),
        uploader=info.get("uploader", "Unknown"),
        duration=info.get("duration", 0),
        url=url,
    )


def download_audio(
    url: str,
    output_dir: Path,
    quality: str = "192",
    fmt: str = "mp3",
) -> Path:
    """Download audio from a URL and convert to the specified format."""
    if quality not in AUDIO_QUALITIES:
        raise ValueError(f"Invalid quality {quality!r}. Choose from: {', '.join(AUDIO_QUALITIES)}")
    if fmt not in AUDIO_FORMATS:
        raise ValueError(f"Invalid format {fmt!r}. Choose from: {', '.join(AUDIO_FORMATS)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": fmt,
                "preferredquality": quality,
            }
        ],
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "download")

    return output_dir / f"{title}.{fmt}"


def download_video(
    url: str,
    output_dir: Path,
    fmt: str = "mp4",
) -> Path:
    """Download video from a URL in the specified format."""
    if fmt not in VIDEO_FORMATS:
        raise ValueError(f"Invalid format {fmt!r}. Choose from: {', '.join(VIDEO_FORMATS)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    opts = {
        "format": f"bestvideo[ext={fmt}]+bestaudio/best[ext={fmt}]/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": fmt,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        info = ydl.extract_info(url, download=True)
        title = info.get("title", "download")

    return output_dir / f"{title}.{fmt}"
