# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Daily Derja (dailyderja.com) is a Hugo static site blog featuring daily reflections and Tunisian Arabic (Darija) language content. It is bilingual (Arabic/English) with RTL/LTR support, audio pronunciation files, and multimedia embeds.

## Common Commands

```bash
# Serve locally with live reload
hugo server

# Serve including draft posts
hugo server -D

# Build for production
hugo build

# Create a new blog post
hugo new content/blog/my-post-title/index.md
```

Hugo version is managed via the GitHub Actions workflow (`.github/workflows/hugo.yml`). No npm/Node.js build step is required — this is a pure Hugo project.

## Architecture

### Config Split

Configuration is split across `hugo.yaml` (root-level: baseURL, theme, image optimization) and `config/_default/` (everything else):

- `config.yaml` — markup settings, taxonomies (`tags`, `categories`, `dialects`, `series`)
- `params.yaml` — Blowfish theme parameters (layout, colors, article display)
- `languages.{ar,en}.yaml` — per-language author profiles and menus
- `menus.en.yaml` / `footer.yaml` — navigation and footer

### Theme

The site uses the [Blowfish](https://blowfish.page/) theme as a git submodule at `themes/blowfish/`. Color scheme is `fire`. Do not edit files inside `themes/blowfish/` — override them via `layouts/` and `assets/` at the project root instead.

### Content Structure

All blog posts live in `content/blog/<slug>/index.md`. Each post directory can include images alongside the markdown. Relevant frontmatter fields:

- `postLang` — language of the post body (`ar`, `en`)
- `showHero`, `heroStyle` — featured image display
- `series` — links the post into a multi-part series (taxonomy)
- `dialects` — dialect taxonomy for filtering
- `description` — the meta/OG/Twitter description (≈150 chars). Falls back to `summary`, then a plain-text excerpt. Write it for search: what the page actually contains. Don't promise lyrics, full translations, native audio, etc. unless the post has them.
- `seoTitle` — optional; replaces `<title>`/`og:title` entirely (no " · The Daily Derja" suffix) so the visible H1 can keep its personality. Keep it ≲60 chars.
- `recommend` — optional list of `{slug, why}` rendered as "Read it in context" (on guides/music notes) or "Go deeper" (on diary entries). `why` is one specific sentence about what the reader will find there. Missing or draft targets are skipped.
- `audioSource` — `tts` (generated with the daily_derja_tools pipeline), `learner` (Jacob's voice), or `native`. Set it only when known; it renders a one-line label under the post.

Series landing pages live in `content/series/`.

### Custom Layouts & Shortcodes

`layouts/` overrides and extends the Blowfish theme:

- `layouts/partials/head.html` — social image handling
- `layouts/partials/comments.html` — Disqus integration
- `layouts/partials/schema.html` — structured data
- `layouts/shortcodes/audio.html` — Plyr-based audio player (used for pronunciation files)
- `layouts/shortcodes/spotify.html`, `youtube` — media embeds
- `layouts/shortcodes/expression.html` — proverb / set-phrase block: the Arabic (`|` marks the line break), then literal → meaning → when to use it. Params: `ar`, `meaning`, `use` (required); `literal`, `kind="proverb"` (shows «مثل», else «تعبير»), `ipa`, `audio` (optional). Styles under "Expression block" at the end of `assets/css/custom.css`.
- `layouts/shortcodes/ltr.html` — wraps English/LTR text inside RTL pages
- `layouts/shortcodes/subscribe.html` — email signup card (follow.it) with WhatsApp/Telegram/Discord as a secondary line; markup lives in `layouts/partials/subscribe-card.html`, which the footer also uses (compact variant). The shortcode is **deferred**: wherever it sits in the post, the card renders once, after the article body (`_default/single.html`), so short posts read as one continuous piece. Add `inline="true"` only if a long post genuinely needs it in place. Always English/LTR, even in Arabic posts. Tunisian-only posts automatically get archive wording ("New posts are in Shami now").
- `layouts/partials/read-in-context.html` — curated onward reading from `recommend:` frontmatter (see below). Labels each item as guide / diary entry / listening note, by dialect, and as "Cross-dialect comparison" when it doesn't share the post's dialect.
- `layouts/partials/related.html` — overrides Blowfish: 3 related posts **in the same dialect only** (Tunisian-only posts recommend only archive posts). Ranking lives in the `related:` block of `config/_default/config.yaml`. Skips anything already linked in the body or in `recommend:`.
- `layouts/partials/learning-paths.html` — the four entry points (Shami reading · vocab & grammar · Tunisian vs Levantine · music & listening). Full tiles on home, /start/, /learn/; compact row under every blog post.
- `layouts/partials/audio-source-note.html` — one-line audio provenance label, driven by `audioSource`.

### Assets

- `assets/css/custom.css` — all custom styling (380+ lines). Includes Arabic font imports (Lalezar, Zain), color overrides, RTL/LTR handling, responsive video containers, dark mode variants, and Plyr player theming.
- `assets/js/audio-init.js` — initializes the Plyr audio player
- `static/audio/` — MP3 pronunciation files for Tunisian Arabic vocabulary (referenced by the `audio` shortcode)
- `assets/images/` — featured images for blog posts

### Deployment

GitHub Actions (`.github/workflows/hugo.yml`) builds and deploys to GitHub Pages on every push to `main` and on a daily schedule (midnight UTC). The `static/CNAME` file sets the custom domain.

## Content Inventory

### Dialects

The site pivoted from Tunisian (Derja) to **Shami (Levantine)** as the primary dialect in November 2025. Older posts use `dialects: tunisian`; current posts use `dialects: shami`. Some posts cover both.

Positioning: Shami reading practice leads (homepage H1 = `tagline` in `params.yaml`, nav "Shami Reading" first). The Tunisian posts are the **Tunisian archive**: labelled as such, kept at their URLs, still in the nav. `shami` means general Levantine; the writing leans Palestinian (إشي, مش) but also uses هلّق etc. Don't describe the site as strictly Palestinian/Jordanian.

Analytics events and GA4 custom dimensions are documented in `docs/analytics.md`.

### Categories

`art-media`, `blog-meta`, `daily-life`, `faith-culture`, `family`, `food`, `health`, `language-learning`, `Notes`, `personal`, `photo`, `product`, `tech-and-tools`, `travel`, `work-and-career`, `writing`

### Series

Each series is named **نسمة X** ("Nasmat X" = "a breeze of X"). Posts use `series_order` to sequence within a series.

| Series     | English         | Focus                                                        |
| ---------- | --------------- | ------------------------------------------------------------ |
| نسمة نهار  | Day Breeze      | Daily micro-journal: moods, routines, small life shifts (default) |
| نسمة قصة   | Story Breeze    | Short Shami narratives with an arc (family life, humor)      |
| نسمة مشوار | Journey Breeze  | Trips, walks, commutes, errands                              |
| نسمة صورة  | Picture Breeze  | Single-photo caption stories                                 |
| نسمة نغمة  | Melody Breeze   | Levantine music & ear training                               |
| نسمة كلمة  | Word Breeze     | Language notes: vocab, phrases, grammar, dialect comparisons |
| نسمة طعمة  | Taste Breeze    | Food & drink: coffee, baking, tasting moments                |
| نسمة فكرة  | Idea Breeze     | Ideas & opinions: books, films, games, culture               |
| نسمة تقويم | Calendar Breeze | Jewish holidays and fasts through the year                   |
| Meta       | Meta            | Behind-the-scenes: tools, workflow, site milestones          |

### Common Tag Clusters

- **Language:** `shami-arabic`, `levantine-arabic`, `tunisian`, `ipa`, `grammar`, `vocabulary`, `dialect-comparison`, `dialect-notes`
- **Daily life:** `daily-reflection`, `morning-routine`, `moving`, `family-life`, `job-search`
- **Faith/culture:** `jewish-holidays`, `hanukkah`, `faith-culture`, `el-ghriba-synagogue`
- **Media:** `music`, `spotify-playlist`, `music-discovery`, `video`, `vlog`
- **Tech:** `obsidian`, `notebooklm`, `ckad`, `kubernetes`

### The كلام Section

At the end of each post, there is a "كلام" ("Kalam" = "Words") section that breaks down key Arabic phrases from the post with IPA and English meanings. This is meant to help readers learn useful expressions in context. The table format includes:

| Arabic | IPA | Meaning |
| ------ | --- | ------- |

The Arabic column shows the original phrase in Arabic script, the IPA column provides a phonetic transcription, and the Meaning column gives an English translation or explanation. This section is a key educational component of the site, reinforcing language learning through real-life examples.

Only choose a few phrases that are particularly interesting, idiomatic, or relevant to the post's story. The goal is to provide readers with practical language takeaways that they can use in their own conversations, not to be an exhaustive translation of the entire post.

## Arabic Typography

In Arabic post body text, always use guillemets for quotation marks: «like this» — never straight ASCII quotes `"like this"`. Straight quotes render incorrectly in RTL context.
