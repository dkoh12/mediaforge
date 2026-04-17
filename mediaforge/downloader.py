import yt_dlp
from pathlib import Path
from dataclasses import dataclass

AUDIO_QUALITIES = ("128", "192", "320")
AUDIO_FORMATS = ("mp3", "m4a", "wav", "flac", "opus")
VIDEO_FORMATS = ("mp4", "webm", "mkv")

AUDIO_MIMETYPES = {
    "mp3": "audio/mpeg",
    "m4a": "audio/mp4",
    "wav": "audio/wav",
    "flac": "audio/flac",
    "opus": "audio/ogg",
}
VIDEO_MIMETYPES = {
    "mp4": "video/mp4",
    "webm": "video/webm",
    "mkv": "video/x-matroska",
}


@dataclass
class MediaInfo:
    title: str
    uploader: str
    duration: int   # seconds
    url: str


def format_duration(seconds: int) -> str:
    """Format seconds into H:MM:SS or M:SS string."""
    mins, secs = divmod(seconds, 60)
    hrs, mins = divmod(mins, 60)
    if hrs:
        return f"{hrs}:{mins:02d}:{secs:02d}"
    return f"{mins}:{secs:02d}"


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


def _find_output_file(output_dir: Path, fmt: str) -> Path:
    """Find the actual file yt-dlp wrote (filename may be sanitized)."""
    matches = list(output_dir.glob(f"*.{fmt}"))
    if not matches:
        raise FileNotFoundError(f"No .{fmt} file found in {output_dir}")
    # Return most recently modified in case of multiple
    return max(matches, key=lambda p: p.stat().st_mtime)


def download_audio(
    url: str,
    output_dir: Path,
    quality: str = "192",
    fmt: str = "mp3",
    embed_thumbnail: bool = False,
) -> Path:
    """Download audio from a URL and convert to the specified format."""
    if quality not in AUDIO_QUALITIES:
        raise ValueError(f"Invalid quality {quality!r}. Choose from: {', '.join(AUDIO_QUALITIES)}")
    if fmt not in AUDIO_FORMATS:
        raise ValueError(f"Invalid format {fmt!r}. Choose from: {', '.join(AUDIO_FORMATS)}")

    output_dir.mkdir(parents=True, exist_ok=True)
    output_template = str(output_dir / "%(title)s.%(ext)s")

    postprocessors = [
        {
            "key": "FFmpegExtractAudio",
            "preferredcodec": fmt,
            "preferredquality": quality,
        }
    ]
    if embed_thumbnail:
        postprocessors.append({"key": "EmbedThumbnail"})

    opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "quiet": True,
        "no_warnings": True,
        "writethumbnail": embed_thumbnail,
        "postprocessors": postprocessors,
    }

    with yt_dlp.YoutubeDL(opts) as ydl:
        ydl.extract_info(url, download=True)

    return _find_output_file(output_dir, fmt)


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
        ydl.extract_info(url, download=True)

    return _find_output_file(output_dir, fmt)
