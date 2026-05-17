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

Series landing pages live in `content/series/`.

### Custom Layouts & Shortcodes

`layouts/` overrides and extends the Blowfish theme:

- `layouts/partials/head.html` — social image handling
- `layouts/partials/comments.html` — Disqus integration
- `layouts/partials/schema.html` — structured data
- `layouts/shortcodes/audio.html` — Plyr-based audio player (used for pronunciation files)
- `layouts/shortcodes/spotify.html`, `youtube` — media embeds
- `layouts/shortcodes/ltr.html` — wraps English/LTR text inside RTL pages
- `layouts/shortcodes/join-channels.html`, `followit.html` — community CTAs

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

### Categories

`art-media`, `blog-meta`, `daily-life`, `faith-culture`, `family`, `food`, `health`, `language-learning`, `Notes`, `personal`, `photo`, `product`, `tech-and-tools`, `travel`, `work-and-career`, `writing`

### Series

Each series is named **نسمة X** ("Nasmat X" = "a breeze of X"). Posts use `series_order` to sequence within a series.

| Series      | English         | Focus                                       |
| ----------- | --------------- | ------------------------------------------- |
| نسمة يوميات | Diary Breeze    | General Arabic journaling (catch-all)       |
| نسمة نهار   | Day Breeze      | Daily micro-journal of moods and moments    |
| نسمة كلمة   | Word Breeze     | Quick Shami vocab drops                     |
| نسمة نغمة   | Melody Breeze   | Levantine music & ear training              |
| نسمة صورة   | Picture Breeze  | Single-photo caption stories                |
| نسمة قصة    | Story Breeze    | Short Shami narratives (family life, humor) |
| نسمة نهار   | Day Breeze      | Daily micro-journal                         |
| نسمة قهوة   | Coffee Breeze   | Café/coffee journal                         |
| نسمة طعمة   | Taste Breeze    | Food & tasting moments                      |
| نسمة فكرة   | Idea Breeze     | Light cultural ideas                        |
| نسمة جملة   | Sentence Breeze | One Shami sentence per post                 |
| نسمة لهجة   | Dialect Breeze  | Tunisian vs. Levantine comparisons          |
| نسمة مشوار  | Journey Breeze  | Walks, commutes, errands                    |
| نسمة معنى   | Meaning Breeze  | Cultural nuance reflections                 |
| نسمة لحظة   | Moment Breeze   | One-snapshot posts                          |
| نسمة صوت    | Sound Breeze    | Audio/pronunciation clips                   |
| نسمة شغلة   | Thing Breeze    | Quirky finds and links                      |
| Meta        | Meta            | Behind-the-scenes tools and workflow notes  |

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
