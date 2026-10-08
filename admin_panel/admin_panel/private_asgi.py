"""Public login, protected Django admin panel."""
import mimetypes
import os
from pathlib import Path
from urllib.parse import unquote
import jwt
from django.conf import settings
from django.core.asgi import get_asgi_application
from jwt import PyJWKClient
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "admin_panel.settings.render")
django_application = get_asgi_application()
_issuer = os.environ.get("CF_ACCESS_ISSUER", "").rstrip("/")
_audience = os.environ.get("CF_ACCESS_AUD", "")
_jwks_client = PyJWKClient(f"{_issuer}/cdn-cgi/access/certs") if _issuer and _audience else None
async def _response(send, status: int, body: bytes, content_type: bytes = b"text/plain; charset=utf-8"):
    await send({"type":"http.response.start","status":status,"headers":[(b"content-type",content_type),(b"content-length",str(len(body)).encode())]})
    await send({"type":"http.response.body","body":body})
async def _serve_file(send, root: str, requested_path: str):
    try:
        base=Path(root).resolve(); target=(base/unquote(requested_path)).resolve()
        if not target.is_relative_to(base) or not target.is_file():
            await _response(send,404,b"Not found\n"); return
        body=target.read_bytes()
    except (OSError,ValueError):
        await _response(send,404,b"Not found\n"); return
    await _response(send,200,body,(mimetypes.guess_type(target.name)[0] or "application/octet-stream").encode())
def _valid_access_jwt(token: str) -> bool:
    if not token or not _jwks_client: return False
    try:
        key=_jwks_client.get_signing_key_from_jwt(token).key
        jwt.decode(token,key,algorithms=["RS256"],audience=_audience,issuer=_issuer)
        return True
    except Exception: return False
async def application(scope, receive, send):
    if scope["type"] != "http":
        await django_application(scope,receive,send); return
    path=scope.get("path","/")
    if path=="/health":
        await _response(send,200,b"ok\n"); return
    static_prefix="/"+settings.STATIC_URL.strip("/")+"/"
    if path.startswith(static_prefix):
        await _serve_file(send,settings.STATIC_ROOT,path[len(static_prefix):]); return
    headers=dict(scope.get("headers",[]))
    token=headers.get(b"cf-access-jwt-assertion",b"").decode("ascii","ignore")
    if not _valid_access_jwt(token) and path not in ("/login/","/logout/"):
        await _response(send,404,b"Not found\n"); return
    await django_application(scope,receive,send)
