import click
from pathlib import Path

from .downloader import (
    get_info,
    download_audio,
    download_video,
    format_duration,
    AUDIO_QUALITIES,
    AUDIO_FORMATS,
    VIDEO_FORMATS,
)


@click.group()
@click.version_option()
def main():
    """🎵 mediaforge — download audio and video from YouTube, SoundCloud, and 1000+ sites"""
    pass


@main.command()
@click.argument("url")
@click.option("--quality", "-q", default="192", show_default=True,
              type=click.Choice(AUDIO_QUALITIES), help="Audio bitrate (kbps)")
@click.option("--format", "-f", "fmt", default="mp3", show_default=True,
              type=click.Choice(AUDIO_FORMATS), help="Output audio format")
@click.option("--output", "-o", default=".", type=click.Path(path_type=Path),
              help="Output directory", show_default=True)
@click.option("--thumbnail", "-t", is_flag=True, help="Embed thumbnail as album art")
def audio(url, quality, fmt, output, thumbnail):
    """Download audio from a URL as MP3 or other audio formats."""
    click.echo("🔍 Fetching info...")
    try:
        info = get_info(url)
        click.echo(f"🎵 {info.title}")
        click.echo(f"   by {info.uploader} · {format_duration(info.duration)}")
        thumb_str = " + thumbnail" if thumbnail else ""
        click.echo(f"⬇️  Downloading as {fmt.upper()} ({quality}kbps){thumb_str}...")
        path = download_audio(url, output, quality=quality, fmt=fmt, embed_thumbnail=thumbnail)
        click.echo(f"✅ Saved: {path}")
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
@click.argument("url")
@click.option("--format", "-f", "fmt", default="mp4", show_default=True,
              type=click.Choice(VIDEO_FORMATS), help="Output video format")
@click.option("--output", "-o", default=".", type=click.Path(path_type=Path),
              help="Output directory", show_default=True)
def video(url, fmt, output):
    """Download video from a URL."""
    click.echo("🔍 Fetching info...")
    try:
        info = get_info(url)
        click.echo(f"🎬 {info.title}")
        click.echo(f"   by {info.uploader} · {format_duration(info.duration)}")
        click.echo(f"⬇️  Downloading as {fmt.upper()}...")
        path = download_video(url, output, fmt=fmt)
        click.echo(f"✅ Saved: {path}")
    except Exception as e:
        raise click.ClickException(str(e))


@main.command()
@click.option("--port", "-p", default=5000, show_default=True, help="Port to run the GUI on")
@click.option("--debug", is_flag=True, help="Run in debug mode")
def gui(port, debug):
    """Launch the mediaforge web GUI in your browser."""
    from mediaforge.gui.app import run
    run(port=port, debug=debug)
