# How It Works

## Overview

The `FramesCog` lives in `frames/package/cog.py` and is loaded automatically when BallsDex starts. Because frames are an art-layer concern rather than a game mechanic, the cog works entirely by **monkey-patching** a small set of BallsDex internals at load time and cleanly restoring them when the cog unloads.

No new database tables exist — frame data is stored as `MM-DD-YYYY`-keyed entries inside the existing `Ball.capacity_logic` JSON field.

---

## Data format

Each frame date is stored as a top-level key in `Ball.capacity_logic`:

```json
{
  "05-12-2026": {
    "spawn": "frame_germany_05-12-2026_spawn.png",
    "card":  "frame_germany_05-12-2026_card.png",
    "credits": "Artist Name",
    "catch": "Happy Europe Day!"
  },
  "12-25-2026": {
    "spawn": "frame_germany_12-25-2026_spawn.png",
    "card":  "frame_germany_12-25-2026_card.png",
    "credits": "Another Artist",
    "catch": "Frohe Weihnachten!"
  }
}
```

Keys are always `MM-DD-YYYY`. `spawn` and `card` are relative paths inside `MEDIA_ROOT`; `credits` and `catch` are plain strings. Either `spawn` or `card` (or both) may be absent — only the keys that are present are applied.

**`get_active_frame(capacity_logic)`** is the single lookup helper: it formats today's date as `%m-%d-%Y` and returns the matching dict, or `None` if today has no frame.

---

## Runtime patches

On `cog_load`, `FramesCog._patch()` replaces six points in the BallsDex codebase. All originals are stored in `self._originals` and restored in `cog_unload`.

### 1. `BallInstance.save` and `BallInstance.objects.acreate`

When a new `BallInstance` is created (either synchronously via `.save()` or asynchronously via `.acreate()`), the patch checks whether today has an active frame for the ball being caught. If so, the frame dict is written into `BallInstance.extra_data` before the record is persisted. This is the mechanism that carries frame metadata alongside each instance for its entire lifetime.

### 2. `BallSpawnView.spawn`

When a ball spawns in a channel, the patched `spawn` method checks for an active frame. If `frame["spawn"]` is set, that file is sent as the spawn image instead of the ball's default `wild_card`. The file extension is preserved from the stored path.

### 3. `image_gen.draw_card` (and the alias in `bd_models`)

When a collection card is rendered, `patched_draw_card` reads `ball_instance.extra_data` for a `card` key. If present, the specified image is opened, fitted to the card artwork area, and pasted over the regular artwork. This affects the card shown in `/balls`, trades, and any other place that calls `draw_card`.

### 4. `CountryballFormatter.format_page`

The collection menu formatter is patched to prepend a 🖼️ emoji to the label of any ball whose `extra_data` contains a `card` key, giving players a visual hint that the ball has a frame card.

### 5. `FilteringChoices` + `filter_balls`

A new `frame` member is injected into the `FilteringChoices` enum (the dropdown used by `/balls`). The patched `filter_balls` function handles this new value by filtering the queryset to instances whose ball has today's date key present in `capacity_logic`.

---

## Patch lifecycle

```
Bot starts
    └─ FramesCog loaded
           └─ _patch() called
                  ├─ originals saved to self._originals
                  └─ six patches applied
                         │
                         ▼  (bot running normally)
                         │
Bot stops / cog unloaded
    └─ cog_unload() called
           └─ all six originals restored from self._originals
                  └─ "frame" enum member removed from FilteringChoices
```

Because every patch is reversible, the cog can be safely reloaded (e.g. with `!reload`) without leaving stale references.

---

## Model reference — `FrameBall`

`FrameBall` is a **proxy model** of `Ball` (`models.py`). It creates no new database table; it exists solely to give the Django admin a dedicated `Frames` section separate from the main `Ball` admin. All frame data lives in `Ball.capacity_logic`.

| Admin column | Source |
|---|---|
| **Country** | `ball.country` |
| **Frames** | Count of valid `MM-DD-YYYY` keys in `capacity_logic` |
| **Dates (MM-DD-YYYY)** | Sorted list of those keys |
