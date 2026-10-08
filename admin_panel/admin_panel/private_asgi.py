"""Public web entrypoint; Django admin enforces authentication."""

import mimetypes
import os
from pathlib import Path
from urllib.parse import unquote

from django.conf import settings
from django.core.asgi import get_asgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_panel.settings.render")
django_application = get_asgi_application()


async def _response(send, status: int, body: bytes, content_type: bytes = b"text/plain; charset=utf-8"):
    await send(
        {
            "type": "http.response.start",
            "status": status,
            "headers": [
                (b"content-type", content_type),
                (b"content-length", str(len(body)).encode()),
            ],
        }
    )
    await send({"type": "http.response.body", "body": body})


async def _serve_file(send, root: str, requested_path: str):
    try:
        base = Path(root).resolve()
        target = (base / unquote(requested_path)).resolve()
        if not target.is_relative_to(base) or not target.is_file():
            await _response(send, 404, b"Not found\n")
            return
        body = target.read_bytes()
    except (OSError, ValueError):
        await _response(send, 404, b"Not found\n")
        return
    content_type = mimetypes.guess_type(target.name)[0] or "application/octet-stream"
    await _response(send, 200, body, content_type.encode())


async def application(scope, receive, send):
    if scope["type"] != "http":
        await django_application(scope, receive, send)
        return

    path = scope.get("path", "/")
    if path == "/health":
        await _response(send, 200, b"ok\n")
        return

    static_prefix = "/" + settings.STATIC_URL.strip("/") + "/"
    media_prefix = "/" + settings.MEDIA_URL.strip("/") + "/"
    if path.startswith(static_prefix):
        await _serve_file(send, settings.STATIC_ROOT, path[len(static_prefix) :])
        return
    if path.startswith(media_prefix):
        await _serve_file(send, settings.MEDIA_ROOT, path[len(media_prefix) :])
        return

    await django_application(scope, receive, send)
