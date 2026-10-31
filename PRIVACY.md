# Privacy

The LinkedIn Marketing plugin collects nothing, stores nothing remotely, and
sends nothing to its author. There is no server behind it and no telemetry in
it. Everything below describes what the plugin does on your own machine.

## What stays on your machine

- **`marketing-config.md`** — your company, voice, content pillars and mention
  settings. Written in your project folder, read by the plugin, never sent
  anywhere by it.
- **`posts/`** — the post copy, slide scripts and PDFs the plugin produces.
- **`mentions-log.md`** — which posts you have already commented on, so the next
  run does not comment twice.
- **The install dialog's answers** — company name, website, audience, cadence and
  the mention settings. Claude Code stores these in your own settings; none is
  marked sensitive, and none is a credential.

## What runs, and what it touches

- **The two session-start reminders** (`hooks/nudge.py`) read only those local
  files and print a line to Claude. They make no network request. They read your
  install-dialog answers from the environment Claude Code gives them.
- **`scripts/download.py`** fetches the Canva export URLs handed to it during a
  carousel run, and writes the images into your post folder. It refuses any URL
  that is not `https`.
- **`scripts/build_pdf.py`** stitches those images into a PDF locally.
- **Research** is Claude's own web search and page fetching, using whatever
  permissions you have granted Claude Code. The plugin asks for it; it does not
  perform it.

## Credentials

The plugin holds none, and asks for none.

LinkedIn and Canva are reached through MCP servers **you** add yourself with
`claude mcp add`. Their credentials — a Canva client secret, a LinkedIn browser
session — are held by those servers and by Claude Code's credential storage. They
never pass through this plugin, and nothing in this plugin reads your Claude Code
settings file.

## What is published, and when

Nothing is posted to LinkedIn automatically. Carousels are handed to you as a PDF
to upload yourself. Comments on posts that mention you are written only after you
approve each one individually, with a hard cap per run.

## Third parties

Using the plugin means using LinkedIn and Canva under their own terms and privacy
policies. Their handling of your data is theirs to describe, not ours.
