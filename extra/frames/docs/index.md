# BallsDex Frames

The **Frames** package is a third-party plugin for [BallsDex](https://github.com/Ballsdex-Team/BallsDex-DiscordBot) that adds date-based art overrides for countryballs. When today's date matches a configured frame, the bot automatically swaps the spawn art, collection card, catch phrase, and credits for that ball — with no code changes required.

## Features

- **Date-range frames** — define a frame for a single day or a range of consecutive days using `MM-DD-YYYY` keys.
- **Spawn art override** — replace the wild-card image used when a ball spawns in a channel.
- **Card art override** — replace the collection card artwork shown in `/balls` and trades.
- **Catch phrase and credits** — append custom text to the catch message and display a different credits line.
- **`/balls` filter integration** — a new `frame` filter option is injected into `FilteringChoices` so players can view only balls that carry an active frame.
- **Frame badge in `/balls`** — a 🖼️ icon appears next to balls in the collection menu when a frame card is present.
- **Django admin integration** — frames are managed entirely from the admin panel; no database schema changes are needed.
- **Zero-downtime patches** — the cog monkey-patches the relevant BallsDex internals at load time and cleanly restores them on unload.

## Contents

```{toctree}
:maxdepth: 2
:caption: Getting Started

installation
```

```{toctree}
:maxdepth: 2
:caption: Reference

how-it-works
admin
changelog
```
