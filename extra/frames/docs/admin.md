# Admin Panel

The Frames package adds a **Frames** section to the BallsDex Django admin. Frames are managed entirely through this interface — no direct database edits are needed.

## Accessing the admin

Navigate to your BallsDex admin panel (typically `http://<your-host>/admin/`) and open **Frames → Frames**.

The changelist shows only balls that have at least one configured frame. Balls with no frame entries are hidden.

| Column | Description |
|---|---|
| **Country** | The ball's name. |
| **Frames** | Total number of frame date entries on this ball. |
| **Dates (MM-DD-YYYY)** | Sorted list of every configured date key. |

---

## Adding a frame

Click **Add Frame** (top-right of the changelist). Fill in the form:

| Field | Description |
|---|---|
| **Ball** | The countryball to attach this frame to. |
| **Date from** | The first (or only) date the frame is active. |
| **Date to** | *(Optional)* The last date of a range. Leave blank for a single day. |
| **Spawn art** | *(Optional)* Replacement wild-card image. Leave blank to keep the ball's default spawn art. |
| **Card art** | *(Optional)* Replacement collection card image. Leave blank to keep the ball's default card. |
| **Credits** | Artist credit line displayed on the card. |
| **Catch phrase** | Text appended to the catch message while this frame is active. |

When you submit the form, one `MM-DD-YYYY` entry is written into `Ball.capacity_logic` for each day in the `[date_from, date_to]` range. Uploaded images are stored in `MEDIA_ROOT` under names like `frame_<ball>_MM-DD-YYYY_spawn.png`.

> **Date ranges** create individual per-day keys. A frame set for `05-12-2026 → 05-14-2026` results in three separate keys: `05-12-2026`, `05-13-2026`, and `05-14-2026`.

---

## Editing frames on an existing ball

Click the ball's name in the changelist to open the change view. The page lists every configured frame date. To **add another date** to the same ball, fill in the form at the top and save.

> At this time there is no inline edit for individual dates. To change the art or text for a date that already exists, submit the form again with the same date — the new values will overwrite the old entry.

---

## Deleting a specific date

On the change view for a ball, each listed date has a **Delete** link. Clicking it opens a confirmation page. Confirming removes only that `MM-DD-YYYY` key from `capacity_logic` — all other frame dates on the ball are unaffected.

> The standard Django "delete object" action is disabled for frames. Ball records are not deleted through this admin; only individual date keys can be removed.

---

## Validation rules

The admin enforces the following before saving:

- **Date to** must be on or after **Date from** (when supplied).
- Images must be valid image files (Django's `ImageField` validation applies).

---

## Behaviour notes

- **No restart required.** Frame changes take effect immediately — the next ball spawn, card render, or `/balls` lookup will use the new data.
- **Only today's key is used.** The bot calls `get_active_frame(capacity_logic)` at the moment of each event, so only the entry matching today's `MM-DD-YYYY` is applied. Past and future entries are stored but ignored until their date arrives.
- **Partial frames are valid.** You can omit `spawn_art`, `card_art`, or both. Only the keys present in the entry are applied; missing keys fall back to the ball's defaults.
