"""Tests for mediaforge.downloader — uses mocks to avoid real network calls."""
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock

from mediaforge.downloader import (
    get_info,
    download_audio,
    download_video,
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

def test_download_audio_returns_path(tmp_path):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO

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
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO
        download_audio("https://example.com/video", out)

    assert out.exists()


@pytest.mark.parametrize("fmt", AUDIO_FORMATS)
def test_download_audio_all_formats(tmp_path, fmt):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO
        result = download_audio("https://example.com/video", tmp_path, fmt=fmt)

    assert result.suffix == f".{fmt}"


@pytest.mark.parametrize("quality", AUDIO_QUALITIES)
def test_download_audio_all_qualities(tmp_path, quality):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO
        result = download_audio("https://example.com/video", tmp_path, quality=quality)

    assert result is not None


# ---------------------------------------------------------------------------
# download_video
# ---------------------------------------------------------------------------

def test_download_video_returns_path(tmp_path):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO

        result = download_video("https://example.com/video", tmp_path)

    assert result == tmp_path / "Test Video.mp4"


def test_download_video_invalid_format(tmp_path):
    with pytest.raises(ValueError, match="Invalid format"):
        download_video("https://example.com/video", tmp_path, fmt="avi")


def test_download_video_creates_output_dir(tmp_path):
    out = tmp_path / "videos"
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO
        download_video("https://example.com/video", out)

    assert out.exists()


@pytest.mark.parametrize("fmt", VIDEO_FORMATS)
def test_download_video_all_formats(tmp_path, fmt):
    with patch("yt_dlp.YoutubeDL") as MockYDL:
        instance = MockYDL.return_value.__enter__.return_value
        instance.extract_info.return_value = FAKE_INFO
        result = download_video("https://example.com/video", tmp_path, fmt=fmt)

    assert result.suffix == f".{fmt}"
