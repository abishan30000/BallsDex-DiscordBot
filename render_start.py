"""Render web-service entrypoint for the BallsDex bot."""

import os
import subprocess
import sys
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_panel.settings")
os.environ.setdefault("BALLSDEX_LOG_DIR", "/tmp/ballsdex")
os.environ["BALLSDEXBOT_EXTRA_TOML"] = "/code/config/extra.toml"
if not os.environ.get("BALLSDEXBOT_DB_URL") and os.environ.get("DATABASE_URL"):
    os.environ["BALLSDEXBOT_DB_URL"] = os.environ["DATABASE_URL"]


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path not in ("/", "/health"):
            self.send_error(404)
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"ok\n")

    def log_message(self, format, *args):
        return


def main():
    port = int(os.environ.get("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()

    subprocess.run(
        [sys.executable, "-m", "django", "migrate", "--no-input", "--fake-initial"],
        check=True,
        cwd="/code/admin_panel",
    )

    import django

    django.setup()
    from settings.models import Settings

    setting, _ = Settings.objects.get_or_create(pk=1)
    token = os.environ.get("BALLSDEXBOT_TOKEN")
    if token:
        setting.bot_token = token
        setting.save(update_fields=["bot_token"])
    else:
        print("BALLSDEXBOT_TOKEN is empty; health endpoint is up, waiting for the secret.", flush=True)
        while True:
            time.sleep(3600)

    return subprocess.run(
        [sys.executable, "-m", "ballsdex", "--dev"],
        check=False,
        cwd="/code/admin_panel",
    ).returncode


if __name__ == "__main__":
    raise SystemExit(main())
