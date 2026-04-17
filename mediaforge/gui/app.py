import io
import tempfile
from pathlib import Path
from flask import Flask, request, send_file, render_template, jsonify
from mediaforge.downloader import (
    get_info,
    download_audio,
    download_video,
    format_duration,
    AUDIO_QUALITIES,
    AUDIO_FORMATS,
    VIDEO_FORMATS,
    AUDIO_MIMETYPES,
    VIDEO_MIMETYPES,
)

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html",
                           audio_qualities=AUDIO_QUALITIES,
                           audio_formats=AUDIO_FORMATS,
                           video_formats=VIDEO_FORMATS)


@app.route("/info", methods=["POST"])
def info():
    """Fetch metadata for a URL."""
    url = request.json.get("url", "").strip()
    if not url:
        return jsonify({"error": "No URL provided"}), 400
    try:
        meta = get_info(url)
        return jsonify({
            "title": meta.title,
            "uploader": meta.uploader,
            "duration": format_duration(meta.duration),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/download", methods=["POST"])
def download():
    """Download audio or video and stream back to the browser."""
    url = request.json.get("url", "").strip()
    media_type = request.json.get("type", "audio")
    fmt = request.json.get("format", "mp3")
    quality = request.json.get("quality", "192")

    if not url:
        return jsonify({"error": "No URL provided"}), 400

    try:
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            if media_type == "audio":
                out_path = download_audio(url, tmp_path, quality=quality, fmt=fmt)
                mimetype = AUDIO_MIMETYPES.get(fmt, "application/octet-stream")
            else:
                out_path = download_video(url, tmp_path, fmt=fmt)
                mimetype = VIDEO_MIMETYPES.get(fmt, "application/octet-stream")

            buf = io.BytesIO(out_path.read_bytes())
            buf.seek(0)

            return send_file(
                buf,
                mimetype=mimetype,
                as_attachment=True,
                download_name=out_path.name,
            )
    except Exception as e:
        return jsonify({"error": str(e)}), 500


def run(port: int = 5000, debug: bool = False) -> None:
    print(f"🎵 mediaforge GUI running at http://localhost:{port}")
    app.run(port=port, debug=debug)
