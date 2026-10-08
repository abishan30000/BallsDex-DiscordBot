# How the Cog Works

## Overview

The `Claim` cog lives in `collector/package/cog.py` and is loaded automatically when BallsDex starts. It provides a `/claim` slash-command group whose sub-commands are built at runtime from the `CollectorType` records stored in the database.

---

## Startup — dynamic command registration

When the cog loads (`cog_load`), it:

1. Queries every **enabled** `CollectorType` from the database, pre-fetching the related `source_special` and `award_special` fields.
2. For each type, calls `_make_collector_command` to build an `app_commands.Command` whose name is the type's name converted to lowercase with spaces replaced by underscores (e.g. `"Gold Collector"` → `/claim gold_collector`).
3. Adds each generated command to the `/claim` group and records the command name so it can be cleaned up on unload.
4. Starts the background revocation task (`_check_loop`).

When the cog unloads, all dynamically registered commands are removed and the background task is cancelled.

> **Important:** Adding a new `CollectorType` in the admin panel requires a **bot restart** for the corresponding `/claim` sub-command to appear in Discord.

---

## The `/claim <name> <ball>` command

Each generated sub-command shares the same handler (`_handle_claim`) and follows this flow:

```
Player runs /claim <type> <ball>
        │
        ▼
Does the CollectorType have an award_special configured?
  No  → Error: "no award special configured"
        │
        ▼
Does the player have a profile?
  No  → Error: "catch some balls first"
        │
        ▼
Does the player already own a <ball> with the award_special?
  Yes → Error: "you already have this ball"
        │
        ▼
Count how many source balls the player owns
(filtered to source_special if one is set)
        │
        ▼
Is the count ≥ required_count(ball.rarity)?
  No  → Error: shows how many are needed vs. owned
        │
        ▼
Create a new BallInstance with the award_special  ✓
```

### Threshold calculation

The required number of balls is computed by `CollectorType.required_count(rarity)`:

$$
\text{raw} = \text{min} + \frac{(\text{rarity} - \text{rarity\_min}) \times (\text{max} - \text{min})}{\text{rarity\_max} - \text{rarity\_min}}
$$

The raw value is **clamped** to `[min, max]` and then **rounded to the nearest `gap`**:

$$
\text{required} = \text{round}\!\left(\frac{\text{clamped}}{\text{gap}}\right) \times \text{gap}
$$

**Example** with the default settings (`min=250`, `max=3500`, `gap=50`, `rarity_min=0.05`, `rarity_max=0.80`):

| Ball rarity | Required copies |
|-------------|----------------|
| 0.05 (common) | 250 |
| 0.40 | ~1,900 |
| 0.80 (rare) | 3,500 |

Balls whose rarity falls outside `[rarity_min, rarity_max]` are clamped to the nearest bound.

---

## Background revocation check

`_check_loop` wakes up every **24 hours** and calls `_run_checks`, which:

1. Loads all enabled `CollectorType` records that have an `award_special`.
2. Fetches every `BallInstance` whose special matches one of those award specials — these are the collector balls currently held by players.
3. For each unique `(source_special, player, ball)` combination, counts how many source balls the player owns.
4. For any collector ball where the player's current count is **below** the threshold, sets `deleted = True` on that instance and logs the revocation.

This ensures that players who trade away their source balls lose their collector reward automatically.

---

## Model reference — `CollectorType`

| Field | Type | Default | Description |
|---|---|---|---|
| `name` | `CharField(64)` | — | Display name; also used to derive the slash-command name. Must be unique, and must produce a valid, unique 1-32 character command name once lower-cased with spaces replaced by underscores. |
| `min` | `IntegerField` | `250` | Minimum ball count required (applied at `rarity_min`). |
| `max` | `IntegerField` | `3500` | Maximum ball count required (applied at `rarity_max`). |
| `gap` | `IntegerField` | `50` | Rounding step applied to the interpolated count. |
| `rarity_min` | `FloatField` | `0.05` | Ball rarity value that maps to `min`. |
| `rarity_max` | `FloatField` | `0.80` | Ball rarity value that maps to `max`. |
| `source_special` | `FK → Special` | `null` | If set, only instances with this special count toward the threshold. |
| `award_special` | `FK → Special` | `null` | The special applied to the awarded ball. **Must be set** for `/claim` to work, and must be unique across Collector Types. |
| `enabled` | `BooleanField` | `True` | Disabled types are skipped on cog load and during revocation checks. |
