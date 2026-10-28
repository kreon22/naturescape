#!/usr/bin/env python3
"""Serve Naturescape on your local network.

    python3 serve.py            # http://<this-machine>:8080
    python3 serve.py --port 9000

Besides serving index.html it offers /feed?url=..., a small RSS relay so the
news section does not depend on third-party feed services. The relay only
fetches public http(s) addresses and caches each feed for 30 minutes.
Standard library only; no installs needed.
"""
import argparse
import ipaddress
import socket
import time
import urllib.parse
import urllib.request
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CACHE_SECONDS = 30 * 60
MAX_BYTES = 3 * 1024 * 1024
_cache = {}


def is_public_host(host):
    try:
        infos = socket.getaddrinfo(host, None)
    except socket.gaierror:
        return False
    for info in infos:
        ip = ipaddress.ip_address(info[4][0])
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or ip.is_multicast:
            return False
    return True


def fetch_feed(url):
    hit = _cache.get(url)
    if hit and time.time() - hit[0] < CACHE_SECONDS:
        return hit[1]
    req = urllib.request.Request(url, headers={"User-Agent": "Naturescape/1.0 (+personal dashboard)"})
    with urllib.request.urlopen(req, timeout=10) as resp:
        body = resp.read(MAX_BYTES + 1)
    if len(body) > MAX_BYTES:
        raise ValueError("feed too large")
    _cache[url] = (time.time(), body)
    return body


class Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        if parsed.path != "/feed":
            return super().do_GET()
        url = urllib.parse.parse_qs(parsed.query).get("url", [""])[0]
        target = urllib.parse.urlparse(url)
        if target.scheme not in ("http", "https") or not target.hostname or not is_public_host(target.hostname):
            return self.send_error(400, "Only public http(s) feed URLs are allowed")
        try:
            body = fetch_feed(url)
        except Exception as exc:  # network errors, timeouts, oversize
            return self.send_error(502, f"Could not fetch feed: {exc}")
        self.send_response(200)
        self.send_header("Content-Type", "application/xml; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass  # keep the Pi's journal quiet


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--bind", default="0.0.0.0", help="use 127.0.0.1 to keep it on this machine only")
    args = ap.parse_args()
    server = ThreadingHTTPServer((args.bind, args.port), Handler)
    print(f"Naturescape on http://{socket.gethostname()}.local:{args.port}  (Ctrl+C to stop)")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
