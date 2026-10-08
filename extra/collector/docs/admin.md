# Admin Panel

The Collector package registers a `CollectorType` model in the Django admin panel that ships with BallsDex. This is the primary interface for managing collector configurations — no manual database edits are needed.

## Accessing the admin

Navigate to your BallsDex admin panel (typically `http://<your-host>/admin/`) and open **Collector → Collector types**.

## Creating a Collector Type

Click **Add Collector Type** and fill in the fields:

| Field | Description |
|---|---|
| **Name** | A human-readable label, e.g. `"Gold"`. The `/claim` sub-command name is derived from this (spaces → underscores, lowercased). Must be unique. |
| **Min** | The ball count required for the most common ball (at `rarity_min`). Default: `250`. |
| **Max** | The ball count required for the rarest ball (at `rarity_max`). Default: `3500`. |
| **Gap** | The rounding step applied to the interpolated threshold. Default: `50`. |
| **Rarity min** | The rarity value mapped to `Min`. Default: `0.05`. |
| **Rarity max** | The rarity value mapped to `Max`. Default: `0.80`. |
| **Source special** | *(Optional)* If set, only ball instances that carry this special are counted toward the threshold. Leave blank to count all copies regardless of special. |
| **Award special** | The special that is applied to the ball awarded on a successful `/claim`. **Required** for the command to function. |
| **Enabled** | Uncheck to temporarily disable this collector type without deleting it. |

### Validation rules

The admin enforces the following before saving:

- `min` must be strictly less than `max`.
- `gap` must be a positive integer.
- `rarity_min` must be strictly less than `rarity_max`.
- `name`, lower-cased with spaces replaced by underscores, must be a valid Discord slash
  command name (1-32 characters; letters, numbers, hyphens, and underscores only) and must not
  collide with another Collector Type's derived command name.
- `award_special`, if set, must not already be used by another Collector Type — each award
  special can only map to one Collector Type.

## Editing an existing Collector Type

Changes to **Min**, **Max**, **Gap**, **Rarity min / max**, and **Source special** take effect at the next `/claim` invocation and the next revocation check — no restart required.

Changes to the **Name** or **Award special** of an existing type require a bot restart because the slash command name is baked in at load time.

## Disabling a Collector Type

Unchecking **Enabled** and saving will:

- Exclude the type from the next revocation check (existing award balls will not be revoked solely because the type was disabled).
- Remove the corresponding `/claim` sub-command after the next bot restart.

## Deleting a Collector Type

Deleting a `CollectorType` does **not** automatically revoke award balls that have already been issued. If you want to clean those up, do so manually or disable the type first and let the revocation loop handle it before deleting.
