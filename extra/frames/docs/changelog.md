# Changelog

All notable changes to the Frames package are documented here.

---

## 0.0.2 — 2026-05-14

### Added

- `chance` key (integer, 1–100) in each frame entry stored in `Ball.capacity_logic`. Defaults to `100` (always active) when omitted.
- On spawn, the chance is evaluated with a 1–100 random roll; if the roll exceeds `chance` the frame is skipped for that spawn and the caught ball carries no frame art either.
- **Admin**: `chance` field added to both the *Add Frame* and *Change Frame* forms with validation enforcing the 1–100 range.
- **Admin**: *Chance* column added to the existing-frames table on the change view, displaying the stored value (or `100%` for legacy entries).

---

## 0.0.1 — 2026-05-12

Initial release.

### Added

- `FrameBall` proxy model providing a dedicated **Frames** section in the BallsDex Django admin.
- Custom add and change views for managing date-keyed frame entries stored in `Ball.capacity_logic`.
- Date-range support — a single form submission can write frames across multiple consecutive days (`MM-DD-YYYY` keys).
- Spawn art override — replaces the wild-card image when a ball spawns in a channel.
- Card art override — replaces the collection card artwork rendered by `draw_card`.
- Catch phrase and credits fields — appended to the catch message and displayed on the card for the duration of the frame.
- `🖼️` badge in the `/balls` collection menu for balls carrying a frame card.
- `frame` filter injected into `FilteringChoices` so players can filter their collection to balls with an active frame.
- Runtime monkey-patching of `BallInstance.save`, `BallInstance.objects.acreate`, `BallSpawnView.spawn`, `image_gen.draw_card`, `CountryballFormatter.format_page`, and `filter_balls` — all patches are cleanly restored on cog unload.
