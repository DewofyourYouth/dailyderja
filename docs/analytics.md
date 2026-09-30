# GA4 events on dailyderja.com

For the before/after readout of the 2026-10-01 launch, see `docs/measurement.md`.

GA4 property: `G-Z4E3K7B8ZR` (set in `hugo.yaml`). The tag only loads in production
builds (`hugo.IsProduction` in `layouts/partials/head.html`), so `hugo server` and
`--environment development` builds send nothing.

Every custom event is sent with `gtag("event", …)` from site JS. No email addresses,
form contents, or other personal data are sent — only paths, file names, and fixed labels.

## Events

| Event | Fires when | Parameters | Source |
| --- | --- | --- | --- |
| `followit_subscribe` | The follow.it email form is **submitted** (after the browser's own `required`/email validation passes). One per submit. This is an **attempt** — see below. | `followit_location` (`post-card`, `post-card-tunisian`, `footer`), `signup_status` = `attempt`, `event_label`, `event_category`, `value` = 1 | `layouts/partials/extend-footer.html` |
| `form_submit` | **Not sent by site code.** GA4 enhanced measurement ("Form interactions") logs it automatically for the same follow.it submit. | GA4 built-ins (`form_id`, `form_destination`, …) | GA4 enhanced measurement |
| `channel_click` | WhatsApp / Telegram / Discord link in a signup card clicked. | `channel`, `channel_location` | `layouts/partials/extend-footer.html` |
| `audio_play` | A pronunciation clip starts playing (each press of play, including after a pause). | `audio_file`, `page_path` | `layouts/partials/audio-pron.html`, `/start/` taste card |
| `tutor_page_click` | Any link to `/tutors/` clicked (nav, vocab-table CTA, learn page). | `cta_source`, `link_text`, `link_url` | `assets/js/tutor-cta.js` |
| `tutor_platform_click` | Outbound tutor-platform link on `/tutors/` clicked. | `platform`, `link_text`, `link_url` | `assets/js/tutor-cta.js` |
| `community_click` | `.jc-btn` community button clicked (only if a page renders one). | `platform`, `link_url`, `page_path` | `assets/js/community-cta.js` |
| `recommendation_click` | **New.** A same-site link inside an onward-reading block is clicked. One per click. | `rec_type` (`context`, `related`, `path`), `rec_location` (`article`, `home`, `start`, `learn`), `source_path`, `destination_path` | `assets/js/rec-tracking.js` |

`recommendation_click` blocks:

- `context`: the curated "Read it in context" / "Go deeper" box (`recommend:` frontmatter).
- `related`: the "More Shami reading" / "More from the Tunisian archive" cards.
- `path`: the four learning-path tiles (home, /start/, /learn/) and the compact row under posts.

## Attempt vs. confirmed signup

The follow.it form posts to `api.follow.it` and the reader leaves the site. follow.it
then asks them to confirm by email. The site never sees whether they confirmed.

- `followit_subscribe` (and GA's own `form_submit` for the same submit) = **attempts**.
  Don't add them together: they're two views of one action.
- **Confirmed** subscribers are only available in the follow.it dashboard. Compare
  follow.it's weekly new-subscriber count with the attempt count for a rough
  confirmation rate.
- If `followit_subscribe` is marked as a key event in GA4, rename it in reports to
  "Signup attempt" so it isn't read as a confirmed subscription.

## Custom dimensions to register in GA4

Parameters only appear in standard reports after they're registered
(Admin → Data display → Custom definitions → Create custom dimension, scope **Event**).
Register the ones you want to report on:

| Dimension name | Event parameter | Used by |
| --- | --- | --- |
| Rec type | `rec_type` | `recommendation_click` |
| Rec location | `rec_location` | `recommendation_click` |
| Rec source path | `source_path` | `recommendation_click` |
| Rec destination path | `destination_path` | `recommendation_click` |
| Signup location | `followit_location` | `followit_subscribe` |
| Signup status | `signup_status` | `followit_subscribe` |
| Channel | `channel` | `channel_click` |
| Channel location | `channel_location` | `channel_click` |
| Audio file | `audio_file` | `audio_play` |
| CTA source | `cta_source` | `tutor_page_click` |
| Tutor platform | `platform` | `tutor_platform_click`, `community_click` |

`page_path` (sent by `audio_play` and `community_click`) duplicates GA's built-in page
path dimension. Only register it if you need it in an event-scoped report.

## Testing without polluting production data

- Local builds don't load GA at all. To exercise the events, stub `window.gtag` in the
  browser (e.g. a Playwright init script that records calls) against a local build.
- Don't submit the follow.it form against production to "test" it. That creates a real
  pending subscription and a real `followit_subscribe`. Use GA4 DebugView with a
  local/stubbed build instead.
