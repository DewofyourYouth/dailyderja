# Measuring the Shami-focus launch

The changes from PR #14 went live on **2026-10-01** (merged 02:02 Israel time).
`tools/growth/growth_report.py` compares the days after launch with an equal number of
days right before it: 28 vs 28 at four weeks, 56 vs 56 at eight.
A GitHub Action (`.github/workflows/growth-report.yml`) runs it every Monday. Each run
commits `reports/growth/<date>.md` and `reports/growth/latest.md` and shows the report
on the run's summary page.

## What it measures

| Change | Metric | Source |
| --- | --- | --- |
| Search titles & descriptions | Impressions, clicks, CTR, avg. position for the four priority pages; site totals | Search Console |
| "Read it in context", related, paths | For sessions that land on a blog post: engagement rate, pages per session. `recommendation_click` per 100 post views, by block. | GA4 |
| Signup card moved after the post | `followit_subscribe` attempts, channel clicks, audio plays per 1,000 post views | GA4 |
| Shami-first positioning | Share of blog post views on Shami vs Tunisian-archive posts (dialect read from each post's frontmatter) | GA4 + repo |

Not automated: **confirmed** email subscribers. Check the follow.it dashboard for the
same two windows. follow.it has no API wired up here.

## Baseline you already have (Search Console, 2026-09-01 → 09-28)

| Page | Impressions | Clicks | Avg. position |
| --- | --- | --- | --- |
| /blog/weak/ | 101 | 1 | 9.1 |
| /blog/enough/ | 65 | 0 | 10.7 |
| /blog/shami-tunsi-differences/ | 65 | 0 | 7.4 |
| /blog/bisaraha/ | 29 | 2 | 10.2 |

## How to read it (decided before the results come in)

- **Search:** a title/description change shows up as **CTR at a similar position**. If a
  page's average position moved by more than 2, the report flags the CTR as not comparable.
  Pages under 100 impressions in either window are flagged as noise. At this traffic
  level, clicks going from 0–2 to 5+ on a page is a real signal; ±1 click is not.
- **Onward reading:** success = pages per session for post landings goes up without
  engagement rate falling. `recommendation_click` has no baseline. Use it to see which
  block (context / related / path) earns clicks, and prune the ones that don't.
- **Signups:** moving the card below the post could lower attempts. If attempts per
  1,000 post views fall by more than about a third with at least 30 attempts in a window,
  try `{{< subscribe inline="true" >}}` on the long word guides only (weak, enough, need)
  and leave diary entries as they are.
- **Everything:** traffic is small, so read each change as a direction, not a verdict.
  Seasonality (Jewish holidays in both windows), new posts, and Google updates move numbers
  too. The report can't separate those out.

## One-time setup

1. **Google Cloud:** create (or pick) a project. Enable the *Google Analytics Data API*
   and the *Google Search Console API*.
2. **Service account:** IAM & Admin → Service accounts → Create. No roles needed.
   Keys → Add key → JSON. Keep the file; it's the secret below.
3. **GA4:** Admin → Property access management → add the service account's email as
   **Viewer**. Note the numeric **Property ID** (Admin → Property details; not `G-Z4E3K7B8ZR`).
4. **Search Console:** Settings → Users and permissions → Add user → the service account
   email, **Restricted**. Note the property name exactly as shown: `sc-domain:dailyderja.com`
   for a domain property, or `https://dailyderja.com/` for a URL-prefix one.
5. **GitHub** (repo → Settings → Secrets and variables → Actions):
   - Secret `GOOGLE_SERVICE_ACCOUNT_JSON` = the whole JSON key file
   - Variable `GA4_PROPERTY_ID` = the numeric property ID
   - Variable `GSC_SITE_URL` = the Search Console property from step 4
6. **GA4 custom dimensions:** register at least `rec_type` (event scope). They only
   collect from the day they're registered, so do this first. Full list in `docs/analytics.md`.
7. Actions → *Growth report* → **Run workflow** to check it works. Before 2026-10-04 it
   will say there's no settled post-launch data yet, because Search Console lags about 3 days.

The service account is read-only on both properties. Revoke it any time from the same screens.

## Run locally

```bash
pip install -r tools/growth/requirements.txt
export GOOGLE_SERVICE_ACCOUNT_JSON="$(cat key.json)" GA4_PROPERTY_ID=123456789 GSC_SITE_URL=sc-domain:dailyderja.com
python tools/growth/growth_report.py --stdout                 # as of today
python tools/growth/growth_report.py --today 2026-10-31 --stdout
python -m unittest tools/growth/test_growth_report.py          # offline tests, no credentials
```
