# LinkedIn Marketing

A Claude Code plugin that writes your weekly LinkedIn carousel. It researches
your company and what's happening in your industry, designs the slides in Canva,
writes the post copy, and hands you a PDF you can upload.

It reminds you when the next one is due. You review everything before it goes
anywhere — the plugin never posts to LinkedIn on your behalf.

It can also watch for posts that mention you and comment on them. That part is
off by default, and every comment needs your approval before it is written.

## Install

**First, install `uv`** — the plugin's only prerequisite. It runs the LinkedIn
server, the reminders, and the carousel's PDF step, and it supplies Python
itself, so there is nothing else to install.

**Windows** (PowerShell):
```powershell
irm https://astral.sh/uv/install.ps1 | iex
```
**macOS / Linux:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then, in Claude Code:

```
/plugin marketplace add gxm097/linkedin-marketing-plugin
/plugin install linkedin-marketing@gavin-marketing-tools
```

You'll be asked for your company name, website, and audience during install.

If you installed `uv` in the same terminal session you are running Claude Code
in, restart Claude Code: the plugin's server and reminders start with the
session and won't find `uv` until then.

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
`/plugin configure linkedin-marketing@gavin-marketing-tools` and set **Days between
posts** or **Start the post automatically when due**.

## Commenting on posts that mention you

Off by default. Turn it on with `/plugin configure
linkedin-marketing@gavin-marketing-tools` → **Watch for posts that mention us**, or
by setting **Watch for mentions** to `yes` in the Mentions section of
`marketing-config.md`.

```
/linkedin-marketing:mention-comments
```

It searches for your company name (plus any extra terms you set), drafts a reply
to each post it finds, **verifies which post each link actually opens**, then
shows you the list and waits. Nothing is written until you say which ones to
post. There's a hard cap per run — three by default — on top of whatever you
approve, because LinkedIn restricts accounts that comment at volume.

What goes out is appended to `mentions-log.md` in your project, which is also how
the next run knows not to comment on the same post twice.

### It needs the comment tool

**The published `mcp-server-linkedin` package cannot comment on posts.** Every
tool in it is read-only except `send_message` and `connect_with_person`. The
comment tool lives in a local clone of that server, so this command only works
once the clone is registered:

```
claude mcp add linkedin-dev -- uv run --directory <path-to>/linkedin-mcp-server mcp-server-linkedin --transport stdio
```

Restart the session afterwards so the tool appears. If it isn't there, the
command stops and tells you this instead of trying anything else.

### Why it double-checks every link

LinkedIn's post search returns permalinks that **are not aligned to the results
they sit beside** — the server's own documentation says so. Taken at face value,
that means commenting on a stranger's unrelated post.

So before writing anything, the command opens each link with the comment tool's
dry run, reads back an excerpt of that post's actual text, and keeps the link
only if it contains the exact phrase quoted from the post it was meant for.
Anything it can't match, it drops and tells you about.

### Mention reminders

Same as the carousel reminder: when a check is due, Claude says so the next time
you open the project and offers to run it. The due date comes from the newest
date heading in `mentions-log.md`. Set the cadence with **Days between mention
checks**, or 0 to switch the reminder off.

The reminder stays silent unless **Watch for mentions** is `yes`, so turning the
feature off really does stop it.

## What's included

| | |
|---|---|
| `/linkedin-marketing:linkedin-setup` | Interviews you and writes `marketing-config.md` |
| `/linkedin-marketing:weekly-carousel` | The weekly carousel — research, slides, copy, PDF |
| `/linkedin-marketing:linkedin-post` | A single-image post, for weeks when a carousel is overkill |
| `/linkedin-marketing:mention-comments` | Finds posts that mention you, verifies each, comments on the ones you approve |
| `marketing-researcher` agent | Researches the company and current trends, returns a sourced brief |
| `carousel-writer` agent | Turns the brief into a slide script and post copy |
| `linkedin-post-creator` agent | Turns the brief into a single-image post package |
| `mention-finder` agent | Finds posts mentioning you and drafts a reply for each; has no write tool |
| `canva-carousel` skill | Builds and exports the slides in Canva, stitches the PDF |

## Requirements

- **[uv](https://docs.astral.sh/uv/)** — the only thing you install yourself.
  See [Install](#install) for the one line per platform.
- **Canva account** — Free works; Pro unlocks Brand Templates
- **Web search enabled** in Claude Code, for the research step

You do **not** need Python, pip, Pillow, or Git. Every script in the plugin
declares what it needs in its own header and runs through `uv run --script`,
which fetches both the libraries and an interpreter on first use.

### On Windows

It works on native Windows; you don't need WSL. Two things worth knowing:

- **The first carousel is slow.** `uv` builds the LinkedIn server, and its first
  tool call downloads a ~187 MB browser. Several minutes, once. It has not hung.
- **Signing in to LinkedIn opens a real browser window.** Claude can't do this
  part for you. It usually happens by itself the first time a LinkedIn tool is
  used — a window appears, you sign in, and it carries on. LinkedIn may ask you
  to confirm in its **mobile app**, or show a captcha; solve either in that
  window. Nothing is automated about your account credentials.

## If something goes wrong

**"Run /linkedin-marketing:linkedin-setup first"** — you're in a folder with no `marketing-config.md`.
Open your marketing project folder, or run `/linkedin-marketing:linkedin-setup` here.

**Canva tools failing** — run `/mcp` and re-authorise
`plugin:linkedin-marketing:canva`. Export links from Canva expire after 24 hours,
so if a run was interrupted mid-export, just run it again.

**Carousel marked NOT GENERATED** — Canva couldn't be reached, but the post copy
and slide script were still written. Fix the connection and re-run, or build the
slides by hand from the script in `post.md`.

**"The comment tool isn't available"** — `/mention-comments` needs the local
clone of the LinkedIn MCP server registered; the published package has no
comment tool. See "It needs the comment tool" above, and restart the session
after adding it.

**A mention was found but not commented on** — the command drops any link it
can't match to the post it was meant for, which is deliberate; an unverified
link is how you comment on the wrong post. It tells you which ones it dropped
and why. `comments_unavailable` means the author restricted replies.

**No reminder appearing, ever** — the reminders run through `uv`, so first check
`uv --version` in a terminal. If that works but reminders still don't appear,
restart Claude Code once: hooks are loaded at session start.

**No reminder appearing** — reminders only fire in a folder that has a
`marketing-config.md`, and only once the cadence has elapsed since the newest
*finished* post in `posts/`. A folder with no `carousel.pdf` or `image.png` in it
is treated as an unfinished week, not a completed one.

## Updating

Bump `version` in both `.claude-plugin/marketplace.json` and
`linkedin-marketing/.claude-plugin/plugin.json`, then have users run
`claude plugin update linkedin-marketing`.
