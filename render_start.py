"""Render entrypoint for the BallsDex bot and its private admin panel."""

import os
import subprocess
import sys
import threading

os.environ["DJANGO_SETTINGS_MODULE"] = "admin_panel.settings.render"
os.environ.setdefault("BALLSDEX_LOG_DIR", "/tmp/ballsdex")
os.environ.setdefault("BALLSDEXBOT_EXTRA_TOML", "/code/config/extra.toml")
if os.path.exists("/code/config/extra.toml"):
    os.environ["BALLSDEXBOT_EXTRA_TOML"] = "/code/config/extra.toml"
if not os.environ.get("BALLSDEXBOT_DB_URL") and os.environ.get("DATABASE_URL"):
    os.environ["BALLSDEXBOT_DB_URL"] = os.environ["DATABASE_URL"]


def main():
    import django
    import uvicorn

    subprocess.run(
        [sys.executable, "-m", "django", "migrate", "--no-input", "--fake-initial"],
        check=True,
        cwd="/code/admin_panel",
    )
    django.setup()
    from django.contrib.auth import get_user_model
    from settings.models import Settings

    username = os.environ.pop("DJANGO_SUPERUSER_USERNAME", "").strip()
    password = os.environ.pop("DJANGO_SUPERUSER_PASSWORD", "")
    if username and password:
        User = get_user_model()
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email="", password=password)
            print(f"Created Django superuser {username!r} from one-time bootstrap variables.", flush=True)
        else:
            print(f"Django superuser {username!r} already exists; bootstrap was not applied.", flush=True)
        del password

    setting, _ = Settings.objects.get_or_create(pk=1)
    token = os.environ.get("BALLSDEXBOT_TOKEN")
    bot = None
    if token:
        if setting.bot_token != token:
            setting.bot_token = token
            setting.save(update_fields=["bot_token"])
        bot = subprocess.Popen(
            [sys.executable, "-m", "ballsdex", "--dev"],
            cwd="/code/admin_panel",
        )
    else:
        print("BALLSDEXBOT_TOKEN is empty; the private admin panel is up and the bot is waiting for its token.", flush=True)

    server = uvicorn.Server(
        uvicorn.Config(
            "admin_panel.private_asgi:application",
            host="0.0.0.0",
            port=int(os.environ.get("PORT", "10000")),
            log_config=None,
            proxy_headers=True,
            forwarded_allow_ips="*",
        )
    )

    if bot is not None:
        def stop_web_when_bot_exits():
            bot.wait()
            server.should_exit = True

        threading.Thread(target=stop_web_when_bot_exits, daemon=True).start()

    server.run()
    if bot is not None:
        if bot.poll() is None:
            bot.terminate()
        return bot.wait()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
