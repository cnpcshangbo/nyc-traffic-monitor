#!/usr/bin/env python3
"""
Simple production server for UMDL2 frontend
Serves the built dist/ directory on port 5173
"""

import http.server
import socketserver
import os

PORT = 5173
DIRECTORY = "dist"

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
        # Serve index.html for all non-file routes (SPA routing)
        if not os.path.exists(os.path.join(DIRECTORY, self.path.lstrip('/'))):
            self.path = '/index.html'
        return super().do_GET()

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    with socketserver.TCPServer(("0.0.0.0", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Serving UMDL2 at http://0.0.0.0:{PORT}")
        httpd.serve_forever()