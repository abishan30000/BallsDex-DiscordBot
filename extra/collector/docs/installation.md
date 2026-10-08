# Installation

## Requirements

- A working [BallsDex](https://github.com/laggron42/BallsDex-DiscordBot) instance (v3.0.0 or later).

## 1. Add the package

Open your BallsDex `config/extra.toml` and add the following entry:

```toml
[[ballsdex.packages]]
location = "git+https://github.com/flaree/ballsdex-collector.git@master"
path = "collector"
enabled = true
```

> **Pinning a release** — replace `@master` with a version tag (e.g. `@v0.0.2`) for a stable, reproducible install.

## 2. Start the bot

```bash
python -m ballsdex
```

That's it. On launch the bot will automatically fetch the package, run any pending migrations, register the `Claim` cog, and add one `/claim <name>` sub-command for every enabled `CollectorType` in the database.

## Updating

To update to a newer version, bump the tag in `config/extra.toml` and restart the bot. The bot will pull the new version and apply any new migrations automatically.

> **Note:** Every time you add a new Collector Type through the admin panel you must restart the bot so it can register the corresponding slash command.
