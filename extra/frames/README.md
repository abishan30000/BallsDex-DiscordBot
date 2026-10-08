# Frames

An external BallsDex package that adds a **Frames** section to the admin panel.

Frames are date-keyed art overrides stored in a ball's `capacity_logic` JSON field.
When a frame is active (today's `MM-DD` matches a key) the bot can swap out the
spawn art, collection card, credits, and catch phrase for that ball.

## Structure stored in `capacity_logic`

```json
{
  "MM-DD": {
    "card": "frame_<ball>_MM-DD_card.png",
    "spawn": "frame_<ball>_MM-DD_spawn.png",
    "credits": "Artist name",
    "catch": "Extra catch phrase text"
  }
}
```

## Installation

Add the following block to your `extra.toml`:

```toml
[[ballsdex.packages]]
location = "/code/extra/frames"
path = "frames"
enabled = true
editable = true
```

Then run migrations:

```
python manage.py migrate frames
```
