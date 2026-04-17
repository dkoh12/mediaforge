"""Tests for mediaforge.downloader — uses mocks to avoid real network calls."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mediaforge.downloader import (
    get_info,
    download_audio,
    download_video,
    format_duration,
    MediaInfo,
    AUDIO_QUALITIES,
    AUDIO_FORMATS,
    VIDEO_FORMATS,
)

FAKE_INFO = {
    "title": "Test Video",
    "uploader": "Test Channel",
    "duration": 120,
}


# ---------------------------------------------------------------------------
# format_duration
# ---------------------------------------------------------------------------

def test_format_duration_seconds_only():
    assert format_duration(45) == "0:45"

def test_format_duration_minutes_and_seconds():
    assert format_duration(125) == "2:05"

def test_format_duration_with_hours():
    assert format_duration(3661) == "1:01:01"

def test_format_duration_zero():
    assert format_duration(0) == "0:00"


# ---------------------------------------------------------------------------
# get_info
# ---------------------------------------------------------------------------

def test_get_info_returns_media_info():
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO

        result = get_info("https://example.com/video")

    assert isinstance(result, MediaInfo)
    assert result.title == "Test Video"
    assert result.uploader == "Test Channel"
    assert result.duration == 120
    assert result.url == "https://example.com/video"


def test_get_info_missing_fields():
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = {}

        result = get_info("https://example.com/video")

    assert result.title == "Unknown"
    assert result.uploader == "Unknown"
    assert result.duration == 0


# ---------------------------------------------------------------------------
# download_audio
# ---------------------------------------------------------------------------

def _mock_audio_download(mock_ydl_cls, tmp_path, fmt="mp3"):
    """Helper: simulate yt-dlp writing a file and mock the YDL class."""
    (tmp_path / f"Test Video.{fmt}").write_bytes(b"fake audio")
    instance = mock_ydl_cls.return_value.__enter__.return_value
    instance.extract_info.return_value = FAKE_INFO


def test_download_audio_returns_path(tmp_path):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_audio_download(MockYDL, tmp_path)
        result = download_audio("https://example.com/video", tmp_path)

    assert result == tmp_path / "Test Video.mp3"


def test_download_audio_invalid_quality(tmp_path):
    with pytest.raises(ValueError, match="Invalid quality"):
        download_audio("https://example.com/video", tmp_path, quality="999")


def test_download_audio_invalid_format(tmp_path):
    with pytest.raises(ValueError, match="Invalid format"):
        download_audio("https://example.com/video", tmp_path, fmt="xyz")


def test_download_audio_creates_output_dir(tmp_path):
    out = tmp_path / "new" / "nested"
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        (tmp_path / "new" / "nested").mkdir(parents=True)
        _mock_audio_download(MockYDL, out)
        download_audio("https://example.com/video", out)

    assert out.exists()


@pytest.mark.parametrize("fmt", AUDIO_FORMATS)
def test_download_audio_all_formats(tmp_path, fmt):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_audio_download(MockYDL, tmp_path, fmt=fmt)
        result = download_audio("https://example.com/video", tmp_path, fmt=fmt)

    assert result.suffix == f".{fmt}"


def test_download_audio_embed_thumbnail(tmp_path):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_audio_download(MockYDL, tmp_path)
        result = download_audio("https://example.com/video", tmp_path, embed_thumbnail=True)

    # Check EmbedThumbnail postprocessor was included
    call_kwargs = MockYDL.call_args[0][0]
    pp_keys = [p["key"] for p in call_kwargs["postprocessors"]]
    assert "EmbedThumbnail" in pp_keys
    assert call_kwargs["writethumbnail"] is True
    assert result.suffix == ".mp3"


def test_download_audio_no_thumbnail_by_default(tmp_path):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_audio_download(MockYDL, tmp_path)
        download_audio("https://example.com/video", tmp_path)

    call_kwargs = MockYDL.call_args[0][0]
    pp_keys = [p["key"] for p in call_kwargs["postprocessors"]]
    assert "EmbedThumbnail" not in pp_keys
    assert call_kwargs["writethumbnail"] is False


@pytest.mark.parametrize("quality", AUDIO_QUALITIES)
def test_download_audio_all_qualities(tmp_path, quality):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_audio_download(MockYDL, tmp_path)
        result = download_audio("https://example.com/video", tmp_path, quality=quality)

    assert result is not None


# ---------------------------------------------------------------------------
# download_video
# ---------------------------------------------------------------------------

def _mock_video_download(mock_ydl_cls, tmp_path, fmt="mp4"):
    """Helper: simulate yt-dlp writing a file and mock the YDL class."""
    (tmp_path / f"Test Video.{fmt}").write_bytes(b"fake video")
    instance = mock_ydl_cls.return_value.__enter__.return_value
    instance.extract_info.return_value = FAKE_INFO


def test_download_video_returns_path(tmp_path):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_video_download(MockYDL, tmp_path)
        result = download_video("https://example.com/video", tmp_path)

    assert result == tmp_path / "Test Video.mp4"


def test_download_video_invalid_format(tmp_path):
    with pytest.raises(ValueError, match="Invalid format"):
        download_video("https://example.com/video", tmp_path, fmt="avi")


def test_download_video_creates_output_dir(tmp_path):
    out = tmp_path / "videos"
    out.mkdir()
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_video_download(MockYDL, out)
        download_video("https://example.com/video", out)

    assert out.exists()


@pytest.mark.parametrize("fmt", VIDEO_FORMATS)
def test_download_video_all_formats(tmp_path, fmt):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        _mock_video_download(MockYDL, tmp_path, fmt=fmt)
        result = download_video("https://example.com/video", tmp_path, fmt=fmt)

    assert result.suffix == f".{fmt}"
