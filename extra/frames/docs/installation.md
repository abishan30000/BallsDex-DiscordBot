# Installation

## Requirements

- A working [BallsDex](https://github.com/Ballsdex-Team/BallsDex-DiscordBot) instance (v3.0.0 or later).

## 1. Add the package

Open your BallsDex `config/extra.toml` and add the following entry:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/flaree/ballsdex-frames.git@master"
path = "frames"
enabled = true
```

> **Pinning a release** — replace `@master` with a version tag (e.g. `@v0.0.1`) for a stable, reproducible install.

## 2. Start the bot

```bash
python -m ballsdex
```

On launch the bot will automatically fetch the package, register the `Frames` section in the admin panel, and apply the runtime patches.

> **No migrations needed.** The Frames package stores all data inside the existing `Ball.capacity_logic` JSON field — no new database tables are created.

## Updating

To update to a newer version, bump the tag in `config/extra.toml` and restart the bot. The bot will pull the new version automatically.
