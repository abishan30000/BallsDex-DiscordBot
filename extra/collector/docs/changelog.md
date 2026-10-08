# Changelog

All notable changes to the Collector package are documented here.

---

## 0.0.4 — 2026-09-03

### Fixed

- Fixed the remaining broken `.alist()` calls in `_run_checks()` (the 24-hour revocation
  check). The 0.0.2 fix only covered `cog_load()` — `_run_checks()` still raised
  `AttributeError` on every run through 0.0.3, meaning collector balls were never
  automatically revoked.
- Fixed a `NameError` in `_run_checks()` (`ct_by_name` was left over from the switch to
  `award_special` foreign keys in 0.0.2 and was never renamed to `ct_by_award_id`), which
  would have failed immediately after the `.alist()` fix above.
- The revocation check now uses the bot's user cache before falling back to an API fetch
  when DMing revoked players.

### Added

- Validation preventing a Collector Type from being saved with a `name` that can't become a
  valid, unique Discord slash command name (length/character constraints, and collisions with
  another type's derived command name).
- Validation preventing two Collector Types from sharing the same `award_special`.
- `cog_load()` now skips and logs an individual Collector Type instead of crashing the whole
  `/claim` group if a command fails to register (e.g. pre-existing data saved before the
  validations above existed).

---

## 0.0.2 — 2026-05-05

### Changed

- **Specials are now resolved by foreign key** instead of by name. `source_special` and `award_special` fields on `CollectorType` are proper `ForeignKey` references to the `Special` model, making lookups more reliable and consistent with how BallsDex handles specials elsewhere.

### Fixed

- Fixed broken `.alist()` calls in `cog.py` that prevented async querysets from resolving correctly (contributed by [@dormieriancitizen](https://github.com/dormieriancitizen)).

---

## 0.0.1 — 2026-05-05

Initial release.

### Added

- `CollectorType` Django model with configurable `min`, `max`, `gap`, `rarity_min`, `rarity_max`, `source_special`, and `enabled` fields.
- Dynamic `/claim <name> <ball>` slash commands registered at bot startup — one sub-command per enabled `CollectorType`.
- Rarity-scaled threshold calculation: required ball count is linearly interpolated between `min` and `max` based on the ball's rarity, then rounded to the nearest `gap`.
- Optional `source_special` filter — only ball instances carrying the specified special count toward the threshold.
- 24-hour background revocation loop that removes collector balls from players who no longer meet the threshold.
- Django admin registration for `CollectorType` with list display, filters, and autocomplete for special fields.
