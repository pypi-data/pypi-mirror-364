import json
import sys
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import typer

from .core import list_files, CONFIG
from .loader import parse_file

app = typer.Typer(help="🚧 coral8: zero-config file loader & simple HTTP bridge")

class BridgeHandler(BaseHTTPRequestHandler):
    def _send(self, code: int, payload: dict):
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(payload).encode())

    def do_GET(self):
        p = urlparse(self.path).path
        if p.startswith("/files/"):
            alias = p.split("/files/", 1)[1]
            registry = list_files()
            if alias not in registry:
                return self._send(404, {"detail": f"Alias '{alias}' not found"})
            try:
                data = parse_file(registry[alias]["path"])
                return self._send(200, {"alias": alias, "data": data})
            except Exception as e:
                return self._send(500, {"detail": str(e)})
        if p == "/health":
            files = list_files()
            return self._send(200, {
                "status": "ok",
                "registered_files": len(files),
                "aliases": list(files.keys()),
            })
        return self._send(404, {"detail": "Not found"})

def _start_server(host: str, port: int):
    httpd = HTTPServer((host, port), BridgeHandler)
    httpd.serve_forever()

@app.command("serve")
def serve(
    host: str = "127.0.0.1",
    port: int = 8000,
    background: bool = True,
):
    """
    Start a simple HTTP bridge for your files.
    By default it runs in the background so your shell is free.
    """
    if background:
        t = threading.Thread(target=_start_server, args=(host, port), daemon=True)
        t.start()
        typer.secho(f"🚀 Serving in background at http://{host}:{port}", fg=typer.colors.CYAN)
    else:
        typer.secho(f"🚀 Serving at http://{host}:{port}", fg=typer.colors.CYAN)
        _start_server(host, port)

if __name__ == "__main__":
    app()

