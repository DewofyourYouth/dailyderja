---
name: derja-cover
description: Generate a Daily Derja blog post cover image using the daily_derja_cover_pipeline repo (a sibling repo at ../daily_derja_cover_pipeline) instead of hand-writing an image-gen prompt from scratch. Use this whenever a dailyderja post needs a featured.jpg / cover image / social card — including Step 3 of the /frontmatter command, or any time the user asks to "make a cover", "generate a cover image", "give this post a photo", or similar for a Daily Derja post. Also consult this skill before writing any freeform image-gen prompt for dailyderja content, since the pipeline already bakes in the site's brand rules (style, palette, figure likeness, no-text/border rules) and a hand-written prompt will conflict with or duplicate them.
---

# Daily Derja cover images

Daily Derja covers are never generated from scratch with a freeform prompt — there's a
dedicated repo, `daily_derja_cover_pipeline` (sibling to this one, at
`../daily_derja_cover_pipeline`), that owns the whole brand system: ornate bordered
frames, logo + `dailyderja.com` baked in, Arabic-title overlay, and per-register
palette/medium/figure rules. Your job is to feed it the *content* (a short scene, a
title phrase, which register) — not to specify style, medium, colors, or aspect ratio
yourself. Read that repo's `README.md` and `CLAUDE.md` for the full picture; this skill
just covers the parts that matter for the dailyderja workflow and a couple of gotchas
learned by actually running it.

## Setup

```bash
cd ../daily_derja_cover_pipeline   # or the absolute path if cwd differs
source .venv/bin/activate
```

API keys already live in that repo's `.env`. `python cover.py templates` lists the
current frame registry if you want to double check names/labels.

## 1. Pick the register from the post's `dialects` field

The brand register follows **dialect of the post, not geography of its events**:
- `dialects: shami` → **levantine** templates (`levantine_gold_A`, `levantine_gold_B`,
  `levantine_ablaq_jasmine`, `levantine_damascus_tile`)
- `dialects: tunisian` → **maghrebi** templates (`maghrebi_zellige`,
  `maghrebi_bougainvillea`)

Any of the register's general templates is a fine, free aesthetic choice — they're not
bound to topic. Glance at recently-generated covers (`ls -t covers/`) to avoid using the
same frame three posts in a row.

If the post's `series` is `نسمة كلمة` (Word Breeze), use the dedicated word templates
(`levantine_word_square` / `maghrebi_word_sbs`) and the `cover.py word` subcommand
instead of `prompt` — see the README's "Word series" section.

## 2. Write the `--prompt` as content only, not style

The pipeline's `brand/prompts.py` already injects medium (gouache/ink), atmosphere,
architecture/botanical dressing, palette, and the "no text / no border" instruction for
the chosen register — that's the whole point of the tool. Your `--prompt` should be
**one or two concrete objects drawn from the post's own text**, described plainly:

```bash
python cover.py prompt \
  --prompt "a single surfboard leaning against a low stone wall at dusk near the shore" \
  --title "منظور تاني" \
  --template levantine_gold_A \
  --out <post-slug>.png
```

Don't add photorealistic-vs-illustrated language, color palettes, aspect ratios, or
figure descriptions — all of that is the register's job, and duplicating it in your own
words fights the template instead of complementing it. No human figure by default; only
pass `--with-figure` / `--figure-photo <photo>` if the user explicitly wants a person in
the scene (this switches to a 3-model comparison slate by default — more cost, more
output to review — so don't reach for it reflexively).

**Gotcha — the general-template window is wide (~2.6:1).** A single object placed
off to one side can leave the rest of the window as flat, undecorated cream paper (seen
firsthand: a lone surfboard on the left half left the right half blank). Either describe
**two** objects spread across the width (e.g. "...a surfboard leaning against the left
end of the wall, and a coffee cup on the right end, with jasmine trailing between them")
or add `--extra "fill the entire frame edge-to-edge with the scene; no empty or blank
paper areas"`.

## 3. Title text

`--title` is a short (2–5 word) Arabic phrase rendered large over the art — it is
**not** the frontmatter `title` (which is usually English). Same rule as the frontmatter
command's `pullquote` and `كلام` table: pull it from the post's own body, or write
something that reads naturally as a caption for the scene — never invent unrelated copy.

## 4. Cost awareness

Every `cover.py prompt`/`word`/`photo` call that hits the API is a real, billed
generation — `--print-prompt` does **not** skip the API call, it just also prints the
assembled prompt alongside generating. Default is 1 image (cheap); reference-photo jobs
default to 3 candidates across models. Aim for 1–2 tries; regenerate once if the
composition is broken (see gotcha above), but don't loop indefinitely chasing
perfection.

## 5. Place the result

Blowfish (the dailyderja theme) auto-discovers `featured.*` in a post's bundle dir — no
frontmatter field needed. The pipeline outputs a large PNG (~6-7MB); **actually
re-encode it to JPEG** before placing it as `featured.jpg` — don't just rename the PNG
(a couple of existing posts have a renamed-not-reencoded PNG sitting under a `.jpg`
extension; that's a mistake to fix if you touch those posts, not a convention to copy):

```bash
python3 -c "
from PIL import Image
im = Image.open('covers/<post-slug>.png').convert('RGB')
im.save('../dailyderja/content/blog/<post-slug>/featured.jpg', 'JPEG', quality=92, optimize=True)
"
```

This shrinks the file substantially (~6MB PNG → ~1-1.5MB real JPEG) and makes the
extension honest.
