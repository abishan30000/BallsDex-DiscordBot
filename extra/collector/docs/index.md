# BallsDex Collector

The **Collector** package is a third-party plugin for [BallsDex](https://github.com/Ballsdex-Team/BallsDex-DiscordBot) that adds a collection milestone system. Players who accumulate enough copies of a ball can claim a special variant of that ball as a reward — with thresholds that scale dynamically based on each ball's rarity.

## Features

- **Dynamic `/claim` commands** — one sub-command per Collector Type, registered automatically on bot startup.
- **Rarity-scaled thresholds** — the number of balls required to claim a reward is interpolated linearly between a configurable minimum and maximum based on the ball's rarity value.
- **Source filtering** — optionally restrict which variant (special) of the source ball counts toward the threshold.
- **Award specials** — the claimed reward ball is granted with a configurable special.
- **Automatic revocation** — a background task runs every 24 hours and removes collector balls from players who no longer meet the threshold (e.g. after trading away copies).
- **Django admin integration** — Collector Types can be created and managed directly from the BallsDex admin panel.

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
