import os
import sys
import urllib.request
import urllib.error
from http.server import SimpleHTTPRequestHandler, HTTPServer

PORT = 3000
BACKEND_TARGET = "http://127.0.0.1:8000"
FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), 'frontend'))

class DevProxyHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def end_headers(self):
        # Force no-cache during local development so changes reflect immediately
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        super().end_headers()

    def do_OPTIONS(self):
        if self.path.startswith('/api/'):
            self._proxy_request('OPTIONS')
        else:
            self.send_response(200)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
            self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
            self.end_headers()

    def do_POST(self):
        if self.path.startswith('/api/'):
            self._proxy_request('POST')
        else:
            self.send_error(405, "Method Not Allowed")

    def do_PUT(self):
        if self.path.startswith('/api/'):
            self._proxy_request('PUT')
        else:
            self.send_error(405, "Method Not Allowed")

    def do_DELETE(self):
        if self.path.startswith('/api/'):
            self._proxy_request('DELETE')
        else:
            self.send_error(405, "Method Not Allowed")

    def do_GET(self):
        if self.path.startswith('/api/'):
            self._proxy_request('GET')
        else:
            super().do_GET()

    def _proxy_request(self, method: str):
        target_url = f"{BACKEND_TARGET}{self.path}"
        content_length = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_length) if content_length > 0 else None

        req_headers = {}
        for header, value in self.headers.items():
            if header.lower() not in ['host', 'content-length']:
                req_headers[header] = value

        req = urllib.request.Request(target_url, data=body, headers=req_headers, method=method)
        try:
            with urllib.request.urlopen(req) as response:
                status_code = response.status
                resp_headers = response.getheaders()
                resp_body = response.read()

                self.send_response(status_code)
                for h_name, h_val in resp_headers:
                    if h_name.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                        self.send_header(h_name, h_val)
                self.send_header('Content-Length', str(len(resp_body)))
                self.end_headers()
                self.wfile.write(resp_body)
        except urllib.error.HTTPError as e:
            err_body = e.read()
            self.send_response(e.code)
            for h_name, h_val in e.headers.items():
                if h_name.lower() not in ['content-length', 'transfer-encoding', 'connection']:
                    self.send_header(h_name, h_val)
            self.send_header('Content-Length', str(len(err_body)))
            self.end_headers()
            self.wfile.write(err_body)
        except Exception as ex:
            err_msg = f'{{"detail": "Dev server proxy failed: {str(ex)}"}}'.encode('utf-8')
            self.send_response(502)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(err_msg)))
            self.end_headers()
            self.wfile.write(err_msg)

if __name__ == '__main__':
    print(f"Starting RiceYield Dev Server on port {PORT} with transparent /api/ proxy to {BACKEND_TARGET}...")
    server = HTTPServer(('127.0.0.1', PORT), DevProxyHandler)
    server.serve_forever()
