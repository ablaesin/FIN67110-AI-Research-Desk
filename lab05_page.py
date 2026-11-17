#!/usr/bin/env python3
"""Local Lab 05 page: run the joined desk and display its saved final report."""
from __future__ import annotations

import html
import re
import subprocess
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).parent
RUNS = ROOT / "runs"


def page(body: str) -> bytes:
    return f"""<!doctype html><html><head><meta charset='utf-8'><title>FIN 67110 Desk</title>
<style>body{{max-width:900px;margin:2rem auto;font:16px/1.5 system-ui}}input{{font:inherit}}pre{{white-space:pre-wrap;background:#f4f6f8;padding:1rem}}</style></head>
<body><h1>FIN 67110 One Desk</h1><form method='post'><label>Ticker <input name='ticker' pattern='[A-Za-z]{{1,6}}' required></label><button>Run desk</button></form>
<p>The page runs the fixed-order command. It keeps the saved run when a part fails.</p>{body}</body></html>""".encode()


class Handler(BaseHTTPRequestHandler):
    def respond(self, status: int, body: str) -> None:
        self.send_response(status); self.send_header("Content-Type", "text/html; charset=utf-8"); self.end_headers(); self.wfile.write(page(body))

    def do_GET(self) -> None:
        query = parse_qs(urlparse(self.path).query); run = query.get("run", [""])[0]
        target = RUNS / run / "final_report.md"
        if run and re.fullmatch(r"[a-z0-9_-]+", run) and target.exists():
            self.respond(200, "<h2>Final report</h2><pre>" + html.escape(target.read_text(encoding="utf-8")) + "</pre>")
        else: self.respond(200, "")

    def do_POST(self) -> None:
        length = int(self.headers.get("Content-Length", "0")); data = parse_qs(self.rfile.read(length).decode())
        ticker = data.get("ticker", [""])[0].upper()
        if not re.fullmatch(r"[A-Z]{1,6}", ticker): self.respond(400, "<p>Use a 1–6 letter ticker.</p>"); return
        completed = subprocess.run([sys.executable, str(ROOT / "one_desk.py"), ticker], cwd=ROOT, text=True, capture_output=True)
        output = html.escape(completed.stdout + completed.stderr)
        latest = max(RUNS.glob(f"{ticker.lower()}-*"), default=None, key=lambda path: path.stat().st_mtime)
        link = f"<p><a href='/?run={latest.name}'>Open final report</a></p>" if latest and (latest / "final_report.md").exists() else ""
        self.respond(200 if completed.returncode == 0 else 500, f"<h2>Desk output</h2><pre>{output}</pre>{link}")


if __name__ == "__main__":
    server = ThreadingHTTPServer(("127.0.0.1", 8000), Handler)
    print("Open http://127.0.0.1:8000")
    server.serve_forever()
