"""Tiny LAN file server for Chromecast/Nest Hub.

FastAPI stays on 127.0.0.1:8766. The Hub cannot fetch localhost, so this
serves ONLY hashed files from state/captures and state/tts on 0.0.0.0:8767.
"""
from __future__ import annotations

import socket
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

PORT = 8767
ROOT = Path(__file__).resolve().parent / "state"
ALLOWED = (ROOT / "captures", ROOT / "tts")

_server: ThreadingHTTPServer | None = None
_lock = threading.Lock()


def lan_ip() -> str:
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("192.168.18.1", 80))
        return sock.getsockname()[0]
    except OSError:
        return "192.168.18.7"
    finally:
        sock.close()


def base_url() -> str:
    return f"http://{lan_ip()}:{PORT}"


def _safe_file(rel: str) -> Path | None:
    name = Path(unquote(rel)).name
    if not name or name.startswith(".") or "/" in rel or "\\" in rel:
        return None
    for folder in ALLOWED:
        candidate = (folder / name).resolve()
        try:
            candidate.relative_to(folder.resolve())
        except ValueError:
            continue
        if candidate.is_file():
            return candidate
    return None


class _Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003
        return

    def do_GET(self) -> None:  # noqa: N802
        rel = self.path.split("?", 1)[0].lstrip("/")
        if rel.startswith("media/"):
            rel = rel[len("media/") :]
        path = _safe_file(rel)
        if path is None:
            self.send_error(404)
            return
        data = path.read_bytes()
        mime = "application/octet-stream"
        if path.suffix == ".jpg":
            mime = "image/jpeg"
        elif path.suffix == ".mp3":
            mime = "audio/mpeg"
        elif path.suffix == ".mp4":
            mime = "video/mp4"
        self.send_response(200)
        self.send_header("Content-Type", mime)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)


def ensure() -> str:
    """Start once. Returns http://<lan>:8767"""
    global _server
    with _lock:
        if _server is None:
            httpd = ThreadingHTTPServer(("0.0.0.0", PORT), _Handler)
            thread = threading.Thread(target=httpd.serve_forever, daemon=True, name="loona-media-lan")
            thread.start()
            _server = httpd
    return base_url()


def url_for(path: Path) -> str:
    ensure()
    return f"{base_url()}/media/{path.name}"
