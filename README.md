# LinkedIn Marketing

A Claude Code plugin that writes your weekly LinkedIn carousel. It researches
your company and what's happening in your industry, designs the slides in Canva,
writes the post copy, and hands you a PDF you can upload.

It reminds you when the next one is due. You review everything before it goes
anywhere — the plugin never posts to LinkedIn on your behalf.

## Install

```
/plugin marketplace add don-mccraw/linkedin-marketing-plugin
/plugin install linkedin-marketing@don-marketing-tools
```

You'll be asked for your company name, website, and audience during install.

Testing a local copy instead:

```
/plugin marketplace add ./linkedin-marketing-plugin
/plugin install linkedin-marketing@don-marketing-tools
```

## Set up (once, about five minutes)

1. **Connect Canva.** Run `/mcp`, choose `plugin:linkedin-marketing:canva`, and
   sign in. The plugin already knows the address — you just approve it.
2. **Open the project folder** where you want your posts saved, and run
   `/linkedin-marketing:linkedin-setup`. It interviews you, reads your website, checks what your
   Canva plan can do, and writes `marketing-config.md`.
3. **Edit `marketing-config.md`** whenever you like. It holds your voice, your
   three content pillars, your banned words, and your brand colors. This file is
   yours — plugin updates never overwrite it.

### Canva plans

Carousels work on **Canva Free**. If you're on **Canva Pro** or above, the plugin
will use one of your Brand Templates instead, which makes the slides properly
on-brand and consistent week to week. Setup detects which applies.

To use a Brand Template, make a 1080×1080 template in Canva and tag its text
fields under **Apps → Bulk Create → Labels**. Setup will find it from there.

## Use

```
/linkedin-marketing:weekly-carousel
```

Or with a topic: `/linkedin-marketing:weekly-carousel our new SOC training`

It will:

1. Research your company and the last 30 days of industry news
2. Offer you three angles — **you pick one**
3. Write the slide script and the post copy
4. Build the slides in Canva and export them
5. Stitch them into one `carousel.pdf`

You get a folder like `posts/2026-10-26-soc-training-gap/`:

| File | What it is |
|---|---|
| `post.md` | The post copy, hashtags, alt text, first comment, and step-by-step upload instructions |
| `carousel.pdf` | The carousel — upload this to LinkedIn as a document |
| `slides/` | The individual slide images |
| `brief.md` | The research and sources behind the post |

### Posting it

LinkedIn carousels are **document posts**. On LinkedIn: **Start a post** → the
document icon (or **…** → **Add a document**) → upload `carousel.pdf` → enter the
document title from `post.md`. Paste the post copy, add the alt text, publish,
then add the first comment. `post.md` spells this out each time.

### Weekly reminders

When a post is due, Claude tells you the next time you open this project and
offers to run it. Nothing happens without your say-so.

The "due" date comes from the newest folder in `posts/` that actually contains
a finished graphic (`carousel.pdf`, or `image.png` for a single-image post), so
don't rename those folders. A run that produced copy but no graphic doesn't
count as done — you'll still be reminded.
To change the cadence, or to have it start automatically instead of asking, run
`/plugin configure linkedin-marketing@don-marketing-tools` and set **Days between
posts** or **Start the post automatically when due**.

## What's included

| | |
|---|---|
| `/linkedin-marketing:linkedin-setup` | Interviews you and writes `marketing-config.md` |
| `/linkedin-marketing:weekly-carousel` | The weekly carousel — research, slides, copy, PDF |
| `/linkedin-marketing:linkedin-post` | A single-image post, for weeks when a carousel is overkill |
| `marketing-researcher` agent | Researches the company and current trends, returns a sourced brief |
| `carousel-writer` agent | Turns the brief into a slide script and post copy |
| `linkedin-post-creator` agent | Turns the brief into a single-image post package |
| `canva-carousel` skill | Builds and exports the slides in Canva, stitches the PDF |

## Requirements

- **Canva account** — Free works; Pro unlocks Brand Templates
- **Web search enabled** in Claude Code, for the research step
- **Python 3 with Pillow** for the PDF step (`python3 -m pip install Pillow`)

## If something goes wrong

**"Run /linkedin-marketing:linkedin-setup first"** — you're in a folder with no `marketing-config.md`.
Open your marketing project folder, or run `/linkedin-marketing:linkedin-setup` here.

**Canva tools failing** — run `/mcp` and re-authorise
`plugin:linkedin-marketing:canva`. Export links from Canva expire after 24 hours,
so if a run was interrupted mid-export, just run it again.

**Carousel marked NOT GENERATED** — Canva couldn't be reached, but the post copy
and slide script were still written. Fix the connection and re-run, or build the
slides by hand from the script in `post.md`.

**No reminder appearing** — reminders only fire in a folder that has a
`marketing-config.md`, and only once the cadence has elapsed since the newest
*finished* post in `posts/`. A folder with no `carousel.pdf` or `image.png` in it
is treated as an unfinished week, not a completed one.

## Updating

Bump `version` in both `.claude-plugin/marketplace.json` and
`linkedin-marketing/.claude-plugin/plugin.json`, then have users run
`claude plugin update linkedin-marketing`.
