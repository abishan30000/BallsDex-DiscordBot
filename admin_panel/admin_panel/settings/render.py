"""Production settings for the Render-hosted BallsDex admin panel."""

import os

from .production_base import *  # noqa: F403

DEBUG = False
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

public_host = os.environ.get("ADMIN_PUBLIC_HOST", "")
render_host = os.environ.get("RENDER_EXTERNAL_HOSTNAME", "")
ALLOWED_HOSTS = [host for host in (public_host, render_host, "localhost", "127.0.0.1") if host]
CSRF_TRUSTED_ORIGINS = [f"https://{public_host}"] if public_host else []

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
MIDDLEWARE.append("admin_panel.middleware.SecurityHeadersMiddleware")
