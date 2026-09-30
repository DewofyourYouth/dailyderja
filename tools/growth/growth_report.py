#!/usr/bin/env python3
"""Before/after growth report for the Shami-focus launch (merged 2026-10-01).

Pulls Search Console and GA4 numbers for two equal-length windows — the N days
after launch and the N days right before it — and writes a Markdown report.
N grows with time since launch (capped at --max-days), so the 4-week run compares
28 vs 28 days and the 8-week run 56 vs 56.

Everything except the two API calls is local and pure: which dialect a page is in
comes from content/blog/*/index.md, and all rates are computed here.

Env:
  GOOGLE_SERVICE_ACCOUNT_JSON  service-account key (JSON text) with read access
                               to the GA4 property and the Search Console site
  GA4_PROPERTY_ID              numeric GA4 property id (not the G-… measurement id)
  GSC_SITE_URL                 Search Console property, e.g. sc-domain:dailyderja.com
                               or https://dailyderja.com/

Usage:
  python tools/growth/growth_report.py --out reports/growth
  python tools/growth/growth_report.py --today 2026-10-29 --stdout
"""

from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import pathlib
import re
import sys
import urllib.parse

LAUNCH = dt.date(2026, 10, 1)
PRIORITY_PAGES = [
    "/blog/weak/",
    "/blog/enough/",
    "/blog/shami-tunsi-differences/",
    "/blog/bisaraha/",
]
EVENTS = [
    "followit_subscribe",
    "form_submit",
    "recommendation_click",
    "channel_click",
    "audio_play",
    "tutor_page_click",
]
GSC_LAG_DAYS = 3  # Search Console data settles ~2–3 days behind
POSITION_SHIFT = 2.0  # beyond this, a CTR change is mostly a ranking change
MIN_IMPRESSIONS = 100  # below this, page CTR is noise
MIN_EVENTS = 30

REPO = pathlib.Path(__file__).resolve().parents[2]
SCOPES = [
    "https://www.googleapis.com/auth/webmasters.readonly",
    "https://www.googleapis.com/auth/analytics.readonly",
]


# ---------------------------------------------------------------- windows


def windows(today: dt.date, launch: dt.date = LAUNCH, max_days: int = 56):
    """Equal-length (pre, post) date windows, inclusive. Post ends GSC_LAG_DAYS ago."""
    last = today - dt.timedelta(days=GSC_LAG_DAYS)
    n = min(max_days, (last - launch).days + 1)
    if n < 1:
        raise SystemExit(
            f"No settled post-launch data yet (launch {launch}, today {today})."
        )
    post = (launch, launch + dt.timedelta(days=n - 1))
    pre = (launch - dt.timedelta(days=n), launch - dt.timedelta(days=1))
    return pre, post


# ---------------------------------------------------------------- dialects (local)


def page_dialects(
    content_dir: pathlib.Path = REPO / "content" / "blog",
) -> dict[str, str]:
    """Map /blog/<slug>/ → 'shami' | 'tunisian' | 'other' from post frontmatter.

    Posts tagged with both dialects count as shami (they're Shami guides with a
    Tunisian comparison)."""
    out = {}
    for md in content_dir.glob("*/index.md"):
        text = md.read_text(encoding="utf-8")
        m = re.match(r"---\n(.*?)\n---", text, re.S)
        fm = m.group(1) if m else ""
        slug = md.parent.name
        s = re.search(r"^slug:\s*['\"]?([^'\"\n]+)", fm, re.M)
        if s:
            slug = s.group(1).strip()
        block = re.search(r"^dialects:\s*\n((?:\s+-\s*.+\n?)+)", fm, re.M)
        ds = re.findall(r"-\s*(\w+)", block.group(1)) if block else []
        kind = "shami" if "shami" in ds else "tunisian" if "tunisian" in ds else "other"
        out[f"/blog/{slug}/"] = kind
    return out


def path_of(url_or_path: str) -> str:
    p = urllib.parse.urlparse(url_or_path).path or "/"
    return p if p.endswith("/") else p + "/"


# ---------------------------------------------------------------- API calls


class Google:
    def __init__(self, key_json: str):
        from google.oauth2 import service_account  # noqa: deferred so tests run without deps
        from google.auth.transport.requests import AuthorizedSession

        creds = service_account.Credentials.from_service_account_info(
            json.loads(key_json), scopes=SCOPES
        )
        self.session = AuthorizedSession(creds)

    def post(self, url: str, body: dict) -> dict:
        r = self.session.post(url, json=body, timeout=60)
        if r.status_code >= 400:
            raise RuntimeError(f"{r.status_code} from {url}: {r.text[:500]}")
        return r.json()

    # Search Console: one row per page
    def gsc_pages(self, site: str, start: dt.date, end: dt.date) -> list[dict]:
        url = (
            "https://searchconsole.googleapis.com/webmasters/v3/sites/"
            f"{urllib.parse.quote(site, safe='')}/searchAnalytics/query"
        )
        data = self.post(
            url,
            {
                "startDate": start.isoformat(),
                "endDate": end.isoformat(),
                "dimensions": ["page"],
                "rowLimit": 5000,
            },
        )
        return [
            {
                "page": path_of(r["keys"][0]),
                "clicks": r["clicks"],
                "impressions": r["impressions"],
                "position": r["position"],
            }
            for r in data.get("rows", [])
        ]

    # GA4: generic runReport → list of {dim: value, metric: number}
    def ga4(
        self,
        prop: str,
        start: dt.date,
        end: dt.date,
        dims: list[str],
        metrics: list[str],
        dim_filter: dict | None = None,
    ) -> list[dict]:
        body = {
            "dateRanges": [
                {"startDate": start.isoformat(), "endDate": end.isoformat()}
            ],
            "dimensions": [{"name": d} for d in dims],
            "metrics": [{"name": m} for m in metrics],
            "limit": 100000,
        }
        if dim_filter:
            body["dimensionFilter"] = dim_filter
        data = self.post(
            f"https://analyticsdata.googleapis.com/v1beta/properties/{prop}:runReport",
            body,
        )
        rows = []
        for r in data.get("rows", []):
            row = {d: v["value"] for d, v in zip(dims, r.get("dimensionValues", []))}
            row.update(
                {
                    m: float(v["value"])
                    for m, v in zip(metrics, r.get("metricValues", []))
                }
            )
            rows.append(row)
        return rows


def begins(field: str, value: str) -> dict:
    return {
        "filter": {
            "fieldName": field,
            "stringFilter": {"matchType": "BEGINS_WITH", "value": value},
        }
    }


def in_list(field: str, values: list[str]) -> dict:
    return {"filter": {"fieldName": field, "inListFilter": {"values": values}}}


def fetch_window(g: Google, prop: str, site: str, start: dt.date, end: dt.date) -> dict:
    """Everything the report needs for one window, as plain data."""
    w = {
        "gsc": g.gsc_pages(site, start, end),
        "views": g.ga4(
            prop,
            start,
            end,
            ["pagePath"],
            ["screenPageViews"],
            begins("pagePath", "/blog/"),
        ),
        "landing": g.ga4(
            prop,
            start,
            end,
            ["landingPage"],
            ["sessions", "engagedSessions", "screenPageViews"],
            begins("landingPage", "/blog/"),
        ),
        "events": g.ga4(
            prop,
            start,
            end,
            ["eventName"],
            ["eventCount"],
            in_list("eventName", EVENTS),
        ),
        "rec_types": None,
        "notes": [],
    }
    # Needs the rec_type custom dimension registered in GA4; skip quietly if not.
    try:
        w["rec_types"] = g.ga4(
            prop,
            start,
            end,
            ["customEvent:rec_type"],
            ["eventCount"],
            in_list("eventName", ["recommendation_click"]),
        )
    except RuntimeError as e:
        w["notes"].append(
            "rec_type breakdown unavailable (register the `rec_type` custom dimension in GA4). "
            + str(e).split(":")[0]
        )
    return w


# ---------------------------------------------------------------- pure summaries


def summarize(w: dict, dialects: dict[str, str]) -> dict:
    gsc = {r["page"]: r for r in w["gsc"]}
    blog_views = sum(r["screenPageViews"] for r in w["views"])
    by_dialect = {"shami": 0.0, "tunisian": 0.0, "other": 0.0}
    for r in w["views"]:
        by_dialect[dialects.get(path_of(r["pagePath"]), "other")] += r[
            "screenPageViews"
        ]
    sessions = sum(r["sessions"] for r in w["landing"])
    engaged = sum(r["engagedSessions"] for r in w["landing"])
    landing_views = sum(r["screenPageViews"] for r in w["landing"])
    events = {e: 0.0 for e in EVENTS}
    for r in w["events"]:
        events[r["eventName"]] = r["eventCount"]
    return {
        "pages": {
            p: gsc.get(p, {"clicks": 0, "impressions": 0, "position": None})
            for p in PRIORITY_PAGES
        },
        "gsc_total": {
            "clicks": sum(r["clicks"] for r in w["gsc"]),
            "impressions": sum(r["impressions"] for r in w["gsc"]),
        },
        "blog_views": blog_views,
        "by_dialect": by_dialect,
        "landing": {"sessions": sessions, "engaged": engaged, "views": landing_views},
        "events": events,
        "rec_types": {
            r["customEvent:rec_type"]: r["eventCount"]
            for r in (w.get("rec_types") or [])
        },
        "notes": w.get("notes", []),
    }


def rate(num: float, den: float, per: float = 1.0) -> float | None:
    return (num / den * per) if den else None


def fmt(x, pct=False, digits=1):
    if x is None:
        return "–"
    return (
        f"{x * 100:.{digits}f}%"
        if pct
        else f"{x:,.{digits}f}"
        if isinstance(x, float) and x % 1
        else f"{x:,.0f}"
    )


def delta(a, b, pct_points=False):
    if a is None or b is None:
        return "–"
    if pct_points:
        return f"{(b - a) * 100:+.1f} pts"
    if a == 0:
        return "new" if b else "0"
    return f"{(b - a) / a * 100:+.0f}%"


# ---------------------------------------------------------------- report


def render(pre: dict, post: dict, win_pre, win_post, generated: dt.date) -> str:
    n = (win_post[1] - win_post[0]).days + 1
    L = [
        f"# Growth report — {generated.isoformat()}",
        "",
        f"Launch: **{LAUNCH}** · comparing **{n} days after** ({win_post[0]} → {win_post[1]}) "
        f"with **{n} days before** ({win_pre[0]} → {win_pre[1]}).",
        "",
        "Small numbers: treat changes as directional. Rows marked ⚠ are too small or confounded to call.",
        "",
        "## 1. Search previews (Search Console)",
        "",
        "| Page | Impr. before → after | Clicks before → after | CTR before → after | Avg pos. before → after | Read |",
        "|---|---|---|---|---|---|",
    ]
    for p in PRIORITY_PAGES:
        a, b = pre["pages"][p], post["pages"][p]
        ca, cb = (
            rate(a["clicks"], a["impressions"]),
            rate(b["clicks"], b["impressions"]),
        )
        pa, pb = a["position"], b["position"]
        flags = []
        if min(a["impressions"], b["impressions"]) < MIN_IMPRESSIONS:
            flags.append("⚠ <100 impr.")
        if pa and pb and abs(pb - pa) > POSITION_SHIFT:
            flags.append("⚠ ranking moved; CTR not comparable")
        read = "; ".join(flags) or f"CTR {delta(ca, cb, pct_points=True)}"
        L.append(
            f"| `{p}` | {fmt(a['impressions'])} → {fmt(b['impressions'])} | {fmt(a['clicks'])} → {fmt(b['clicks'])} "
            f"| {fmt(ca, pct=True)} → {fmt(cb, pct=True)} | {fmt(pa)} → {fmt(pb)} | {read} |"
        )
    ta, tb = pre["gsc_total"], post["gsc_total"]
    L += [
        "",
        f"Whole site: {fmt(ta['impressions'])} → {fmt(tb['impressions'])} impressions "
        f"({delta(ta['impressions'], tb['impressions'])}), {fmt(ta['clicks'])} → {fmt(tb['clicks'])} clicks "
        f"({delta(ta['clicks'], tb['clicks'])}), CTR {fmt(rate(ta['clicks'], ta['impressions']), pct=True)} → "
        f"{fmt(rate(tb['clicks'], tb['impressions']), pct=True)}.",
        "",
        "## 2. Onward reading (GA4, sessions that land on a blog post)",
        "",
        "| | Before | After | Change |",
        "|---|---|---|---|",
    ]
    la, lb = pre["landing"], post["landing"]
    rows = [
        ("Sessions landing on a post", la["sessions"], lb["sessions"], False),
        (
            "Engagement rate",
            rate(la["engaged"], la["sessions"]),
            rate(lb["engaged"], lb["sessions"]),
            True,
        ),
        (
            "Pages per session",
            rate(la["views"], la["sessions"]),
            rate(lb["views"], lb["sessions"]),
            False,
        ),
    ]
    for label, a, b, pct in rows:
        L.append(
            f"| {label} | {fmt(a, pct=pct, digits=2 if not pct else 1)} | {fmt(b, pct=pct, digits=2 if not pct else 1)} "
            f"| {delta(a, b, pct_points=pct)} |"
        )
    rc = post["events"]["recommendation_click"]
    L += [
        "",
        f"`recommendation_click` (new, no baseline): **{fmt(rc)}** clicks, "
        f"{fmt(rate(rc, post['blog_views'], 100), digits=2)} per 100 post views.",
    ]
    if post["rec_types"]:
        L.append(
            "By block: "
            + ", ".join(
                f"{k or '(not set)'} {fmt(v)}"
                for k, v in sorted(post["rec_types"].items())
            )
            + "."
        )
    ea, eb = pre["events"], post["events"]
    va, vb = pre["blog_views"], post["blog_views"]
    L += [
        "",
        "## 3. Signups (per 1,000 blog post views)",
        "",
        "| | Before | After | Change |",
        "|---|---|---|---|",
    ]
    for e, label in [
        ("followit_subscribe", "Email signup attempts (`followit_subscribe`)"),
        ("channel_click", "WhatsApp/Telegram/Discord clicks"),
        ("audio_play", "Audio plays"),
    ]:
        a, b = rate(ea[e], va, 1000), rate(eb[e], vb, 1000)
        flag = " ⚠" if max(ea[e], eb[e]) < MIN_EVENTS else ""
        L.append(
            f"| {label} | {fmt(a, digits=2)} ({fmt(ea[e])}) | {fmt(b, digits=2)} ({fmt(eb[e])}) | {delta(a, b)}{flag} |"
        )
    L += [
        "",
        "Attempts only. Confirmed subscribers are in the follow.it dashboard. GA's automatic "
        "`form_submit` is the same action, so don't add it on top.",
        "",
        "## 4. Shami focus (share of blog post views)",
        "",
        "| | Before | After |",
        "|---|---|---|",
    ]
    for d, label in [
        ("shami", "Shami (incl. Shami + Tunisian guides)"),
        ("tunisian", "Tunisian archive"),
        ("other", "Other / untagged"),
    ]:
        L.append(
            f"| {label} | {fmt(rate(pre['by_dialect'][d], va), pct=True)} | {fmt(rate(post['by_dialect'][d], vb), pct=True)} |"
        )
    L += ["", f"Blog post views: {fmt(va)} → {fmt(vb)} ({delta(va, vb)})."]
    notes = sorted(set(pre["notes"] + post["notes"]))
    if notes:
        L += ["", "## Notes", ""] + [f"- {x}" for x in notes]
    return "\n".join(L) + "\n"


# ---------------------------------------------------------------- main


def main(argv=None):
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--today", type=dt.date.fromisoformat, default=dt.date.today())
    ap.add_argument("--max-days", type=int, default=56)
    ap.add_argument(
        "--out", type=pathlib.Path, help="directory for <date>.md and latest.md"
    )
    ap.add_argument("--stdout", action="store_true")
    args = ap.parse_args(argv)

    missing = [
        k
        for k in ("GOOGLE_SERVICE_ACCOUNT_JSON", "GA4_PROPERTY_ID", "GSC_SITE_URL")
        if not os.environ.get(k)
    ]
    if missing:
        raise SystemExit("Missing env: " + ", ".join(missing))

    g = Google(os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"])
    prop, site = os.environ["GA4_PROPERTY_ID"], os.environ["GSC_SITE_URL"]
    win_pre, win_post = windows(args.today, max_days=args.max_days)
    dialects = page_dialects()
    pre = summarize(fetch_window(g, prop, site, *win_pre), dialects)
    post = summarize(fetch_window(g, prop, site, *win_post), dialects)
    md = render(pre, post, win_pre, win_post, args.today)

    if args.out:
        args.out.mkdir(parents=True, exist_ok=True)
        (args.out / f"{args.today.isoformat()}.md").write_text(md, encoding="utf-8")
        (args.out / "latest.md").write_text(md, encoding="utf-8")
    if args.stdout or not args.out:
        sys.stdout.write(md)


if __name__ == "__main__":
    main()
