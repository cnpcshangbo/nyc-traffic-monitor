#!/usr/bin/env python3
"""
Simple production server for UMDL2 frontend
Serves the built dist/ directory (default) on a configurable port.

Usage examples:
  PORT=5173 python3 serve.py
  python3 serve.py --port 5173 --dir dist
"""

import http.server
import socketserver
import os
import argparse
import json

DEFAULT_PORT = int(os.environ.get("PORT", "5173"))
DEFAULT_DIR = os.environ.get("SERVE_DIR", "dist")

VERBOSE = False


class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        # Add cache headers for better performance
        if self.path.endswith(('.js', '.css', '.png', '.jpg', '.svg')):
            self.send_header('Cache-Control', 'public, max-age=31536000')
        elif self.path.endswith('.html'):
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        super().end_headers()

    def do_GET(self):
        # Optional verbose logging
        if VERBOSE:
            client = self.client_address[0]
            print(f"[REQ] {client} GET {self.path}")

        # Lightweight health endpoints
        if self.path in ('/health', '/healthz', '/ready'):
            payload = {"status": "ok"}
            data = json.dumps(payload).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(data)))
            self.end_headers()
            self.wfile.write(data)
            return

        # Serve index.html for all non-file routes (SPA routing)
        if not os.path.exists(os.path.join(DIRECTORY, self.path.lstrip('/'))):
            self.path = '/index.html'
        return super().do_GET()

    def do_HEAD(self):
        if self.path in ('/health', '/healthz', '/ready'):
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return
        return super().do_HEAD()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))

    parser = argparse.ArgumentParser(description="Serve built frontend")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port to bind (default from PORT env or 5173)")
    parser.add_argument("--dir", default=DEFAULT_DIR, help="Directory to serve (default from SERVE_DIR env or 'dist')")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose request logging")
    args = parser.parse_args()

    # Validate directory
    if not os.path.isdir(args.dir):
        raise SystemExit(f"Serve directory not found: {args.dir}. Did you run 'npm run build'? ")

    # Use requested directory
    DIRECTORY = args.dir  # noqa: N816 (keep uppercase for clarity with handler)
    VERBOSE = bool(args.verbose)

    # Create server with socket reuse option
    class ReusableTCPServer(socketserver.TCPServer):
        allow_reuse_address = True

    with ReusableTCPServer(("0.0.0.0", args.port), MyHTTPRequestHandler) as httpd:
        print(f"Serving UMDL2 from '{DIRECTORY}' at http://0.0.0.0:{args.port}")
        if VERBOSE:
            print("Verbose logging enabled. Health endpoint at /health")
        httpd.serve_forever()
