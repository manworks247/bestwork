#!/usr/bin/env python3
import http.server
import socketserver
import os
import urllib.parse

PORT = 3000
ROOT = os.path.dirname(os.path.abspath(__file__))


class PresentationHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=ROOT, **kwargs)

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path.startswith("/download/"):
            fname = os.path.basename(path)
            fpath = os.path.join(ROOT, fname)
            if os.path.isfile(fpath):
                self.send_response(200)
                if fname.endswith(".pptx"):
                    self.send_header(
                        "Content-Type",
                        "application/vnd.openxmlformats-officedocument.presentationml.presentation",
                    )
                elif fname.endswith(".pdf"):
                    self.send_header("Content-Type", "application/pdf")
                else:
                    self.send_header("Content-Type", "application/octet-stream")
                self.send_header("Content-Disposition", f'attachment; filename="{fname}"')
                self.send_header("Content-Length", str(os.path.getsize(fpath)))
                self.end_headers()
                with open(fpath, "rb") as f:
                    self.wfile.write(f.read())
                return

        if path == "/" or path == "/index.html":
            self.path = "/index.html"

        return super().do_GET()


if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("0.0.0.0", PORT), PresentationHandler) as httpd:
        print(f"Serving Zenith-V Presentation UI on http://0.0.0.0:{PORT}")
        httpd.serve_forever()
