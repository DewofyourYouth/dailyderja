# GA4 events on dailyderja.com

GA4 property: `G-Z4E3K7B8ZR` (set in `hugo.yaml`). The tag only loads in production
builds (`hugo.IsProduction` in `layouts/partials/head.html`), so `hugo server` and
`--environment development` builds send nothing.

Every custom event is sent with `gtag("event", …)` from site JS. No email addresses,
form contents, or other personal data are sent — only paths, file names, and fixed labels.

## Events

| Event | Fires when | Parameters | Source |
| --- | --- | --- | --- |
| `newsletter_signup` | The signup card's form is submitted to Brevo in the background (fetch). One per submit, after Brevo replies. | `signup_location` (`post-card`, `post-card-tunisian`, `footer`), `signup_status` (`submitted` = Brevo accepted the address and sent the confirmation email; `error`), `event_label`, `event_category`, `value` (1 for `submitted`, else 0) | `layouts/partials/extend-footer.html` |
| `ebook_download` | The download button on `/welcome/` is clicked (any link with `data-download`). One per click. | `file_name` (`everyday-shami-sample`), `link_url`, `event_label`, `event_category` = `newsletter` | `layouts/partials/extend-footer.html` |
| `file_download` | **Not sent by site code.** GA4 enhanced measurement may also log the same PDF click. It's a second view of the same download; count `ebook_download`. | GA4 built-ins (`file_name`, `link_url`, …) | GA4 enhanced measurement |
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

## Submitted vs. confirmed signup

Signups go to Brevo (form `dailyderja-subscribe`, list "DailyDerja Readers") with double
opt-in. The reader stays on the page; Brevo emails a confirmation link, and clicking it
lands them on `/welcome/`, which has the free Everyday Shami sample.

- `newsletter_signup` with `signup_status` = `submitted` = Brevo accepted the address.
  It is **not** a subscriber yet.
- A **confirmed** subscriber = a page view of `/welcome/` (and the contact appears in the
  Brevo list). `/welcome/` is `noindex` and not linked anywhere on the site, so its views
  are almost entirely confirmations.
- Without JavaScript the form posts straight to Brevo and no event fires.

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
| Signup location | `signup_location` | `newsletter_signup` |
| Signup status | `signup_status` | `newsletter_signup` |
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
- Don't submit the signup form with fake addresses to "test" it. Every submit creates a
  real Brevo contact and sends a real confirmation email; test once with your own address. Use GA4 DebugView with a
  local/stubbed build instead.
