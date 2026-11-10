---
name: canva-carousel
description: Builds LinkedIn graphics in Canva — carousel slides stitched into the single multi-page PDF LinkedIn needs, or a single post image. Starts from the company's own reference designs when the config lists them, so the result looks made by the brand's designer rather than generated. Use when a carousel, slide deck, multi-slide graphic, or single marketing image is needed for a social post.
allowed-tools: Read, Write, Glob, Bash(uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/download.py" *), Bash(uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/build_pdf.py" *)
---

# Canva graphics builder

You turn a slide script (or a single-image spec) into finished graphics in
Canva, export them, and — for a carousel — produce one multi-page PDF.

**Why a PDF:** LinkedIn switched off native multi-image carousels in December
2023. A swipeable carousel is now a *document post* — one multi-page file, one
page per slide. Separate PNGs cannot be posted as a carousel.

**Run this skill in the main conversation**, not inside a subagent. The Canva
tools come from an MCP server, and the plugin's agents are given a fixed tool
list that does not include them.

## What you are given

- A **slide script** (6–10 slides) or a **single-image spec**. Each slide or
  image names a **layout** (a reference design label from the config) and its
  **slot text**: tag, headline lines with the accent line marked, subline, body,
  source line. Older scripts may give a free-form `image` line instead — treat
  that as `generate` mode input.
- An **output directory** (the post package folder).
- The **Image** and **Carousel** sections of `marketing-config.md`.

## What you must produce

In the output directory:
- Carousel: `slides/01.png`, `slides/02.png`, … and `carousel.pdf`
- Single image: `image.png`
- `slides/slides.json` (carousel) or `image.json` (single) —
  `{"mode": "...", "design_ids": [...], "layouts": ["..."], "slides": [{"n": 1, "headline": "...", "file": "01.png"}]}`
- `preview-*.png` for every graphic shown to the user for approval

## Step 1 — Find the Canva tools

Canva may be connected under any server name: `canva` if the user added it with
`claude mcp add`, or an opaque id if it is the claude.ai Canva connector. **Don't
look for a fixed prefix.** Use whichever connected server offers `copy-design`,
`edit-design` and `export-design` (load them with ToolSearch if they are
deferred), and say which server you are using.

If no server offers them, Canva is not connected — skip to **Degrading
gracefully**.

Tool argument names come from each tool's schema. If a call fails on its
arguments, read the error and retry — don't abandon the graphic.

## Step 2 — Pick the mode

Read the config's **Image approach** (fall back to **Canva mode**, then `auto`):

- **reference-copy** — the default whenever the config lists **Reference
  designs**. Copies a design the company's own designer made and rewrites only
  its text. This is what keeps the output from looking generated.
- **brand-template** — a Brand Template is configured and its fields are tagged
  (`get-brand-template-dataset` is non-empty). Autofills it.
- **generate** — nothing else is available. Works on Canva Free, but the result
  looks generated; say so when you fall back to it.

`auto` means: reference-copy if reference designs are listed, else
brand-template if `list-brand-kits` works and a square template exists, else
generate. Record the mode in the JSON.

## Step 3 — Choose layouts (human-made rules)

Generated-looking posts share the same tells: one layout every week, a slogan
for a headline, the same glowing imagery. Avoid them:

1. **Rotate layouts.** Read the previous post folders' `slides.json` /
   `image.json` under the config's **Save posts to** folder and don't reuse the
   layout the last post used. In a carousel, the hook slide and the CTA slide
   may share a layout family, but the body slides should not all be identical
   unless the reference design is itself a carousel.
2. **Respect the layout's text budget.** Each reference page has slots of a
   fixed size. Keep each replacement close to the original's character count
   — a 3-letter line replaced by a 9-letter one will overflow at 200px.
3. **Apply the config's Look to avoid list** to any image you add or generate.
4. **At most one number per graphic, with its source** in the body or a source
   line. Never put an unverified statistic on an image without the package
   flagging it.

## Step 4 — Build

### reference-copy mode
For each graphic:
1. `copy-design` the reference design with only the page you need
   (`page_numbers`). The original stays untouched.
2. `read-design` the copy with `open_transaction: true` and
   `fields: ["design_content", "thumbnails"]`. Note each text element's
   `locator_id` and its **text regions** — one region per style run (a white
   line, an accent line, a letter-spaced subline).
3. `edit-design` with `finalize: "keep_open"`:
   - `update_title` → `DRAFT – <post slug> – <layout label>`
   - one `find_and_replace_text` **per region**, using that region's exact
     current characters as `find_text`. Never `replace_text` a whole styled
     element: it flattens every region to one style and the design stops
     looking like the brand's.
4. **Check the returned thumbnail after every edit call.** Look for overflow,
   wrapped headlines, a stray character on its own line, and wrong colours.
   Matching the original's character count is not enough — letters differ in
   width. If a line wraps, replace it with the spec's fallback (`line ||
   fallback`); if there is none or it still wraps, shorten it yourself and say
   so when you return.
5. **Watch for substring collisions.** `find_and_replace_text` replaces the
   first match: replacing `In 2025` after another line already became
   `In 2025.` hits the wrong one. Replace in an order where no new text
   contains a later `find_text`, or include the trailing `\n` in `find_text`.
6. Background photo: keep the reference's photo unless the config lists an
   **Asset folder**. If it does, `list-folder-items` that folder, pick an image
   that fits the post, and `update_fill` the full-bleed background element with
   it (a real photo beats any stock or generated one).
7. Save the thumbnail as `preview-<n>.png` in the output directory.
8. **Do not commit yet.** See Step 5.

### brand-template mode
1. `get-brand-template-dataset` to learn the field names (tagged in Canva under
   **Apps → Bulk Create → Labels**). An empty dataset means the template is
   untagged: tell the user and fall back.
2. `autofill-design` each graphic, mapping slot text onto fields. Autofill is
   asynchronous — poll until it reports success.

### generate mode
1. `generate-design` from a prompt carrying the slot text, the config's Style,
   Brand colors, Fonts and Look to avoid. If a Brand Kit exists and the user
   has agreed to an on-brand design, pass `brand_kit_id`. It is slow — allow
   up to 60 seconds and don't run many at once.
2. `create-design-from-candidate` for the candidate the user picks.

## Step 5 — Approval gate

Nothing is saved or exported until the user approves it.

1. If the config names a **Drafts folder**, `search-folders` for it
   (`create-folder` if missing) and `move-item-to-folder` each draft design
   there, so drafts never mix with the designer's finished work.
2. Return the preview files, the Canva edit link, and the slot text you used.
3. Stop. The calling command asks the user. On approval, `edit-design` with
   `finalize: "commit"`, then export. If the user wants changes, apply them in
   the same open transaction and preview again. If the transaction has expired,
   open a new one with `read-design` — the copy is still there.

## Step 6 — Export and download

1. `export-design` each approved design as **PNG** at the config's size
   (**Slide size** for a carousel, **Single-image size** for a single image,
   fallback 1080×1080 and 1200×627). Confirm with `get-export-formats` if an
   export is refused.
2. **Download immediately** — Canva's export URLs expire after 24 hours. Pass
   every URL in **slide order**, in one call; the script numbers them `01.png`,
   `02.png`, … itself:
   ```bash
   uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/download.py" <out>/slides "<url-1>" "<url-2>" ...
   ```
   For a single image, download into a scratch folder and move `01.png` to
   `<out>/image.png`.
   Don't reach for `curl`: in Windows PowerShell 5.1 `curl` is an alias for
   `Invoke-WebRequest` and rejects `-fsSL`/`-o`. A 403 or 404 from this script
   means an export expired and has to be redone — it says so.
3. Respect the rate limit: `export-design` allows 20 requests per minute. For a
   10-slide deck, pace the calls.
4. If an export fails with `license_required`, a premium Canva element is in
   the design. Tell the user which slide, and either swap the element or carry
   on without that slide's image.

## Step 7 — Stitch the PDF (carousel only)

```bash
uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/build_pdf.py" <out>/slides -o <out>/carousel.pdf
```

The script enforces LinkedIn's 300-page and 100 MB caps and warns if slide sizes
differ. It embeds each PNG losslessly rather than re-encoding it.

**`uv run --locked --script`, not `python3`.** The script's own header declares img2pdf
and Pillow, so `uv` fetches them — and an interpreter if the machine has none.
There is nothing for the user to install. A bare `python3` both skips that and
does not exist on Windows, where the python.org installer provides `python.exe`
and Windows ships an alias named `python3.exe` that opens the Microsoft Store.

## Step 8 — Check before returning

- One PNG per slide in the script, correctly numbered and in order
- `carousel.pdf` exists, opens, and has exactly as many pages as there are slides
- Slide 1 is the hook slide — the one that stops the scroll
- Text is legible at phone size and nothing overflows its slot
- The layout differs from the previous post's
- Nothing from the config's **Avoid in images** or **Look to avoid** lists appears
- The JSON records the mode, design ids and layouts used

## Degrading gracefully

Never abandon the week's post because Canva failed. If no Canva server is
connected, it isn't authorised, or it is erroring:

1. Write the JSON with the full slide script, the layouts and slot text you
   would have used.
2. Create no `carousel.pdf` / `image.png`.
3. Report clearly: which step failed, the exact error, and that the post copy is still usable.
4. If it is an auth problem, say Canva needs connecting and point at the
   README's **Connect Canva** step: either the claude.ai Canva connector, or a
   Canva app's own client ID and secret through `claude mcp add`, then `/mcp` →
   `canva` → sign in. Authorising `plugin:linkedin-marketing:canva` will not
   work: it fails with "does not support dynamic client registration".

The post copy ships either way. A missing graphic is a delay; a missing post is a missed week.

## Single images

For a single post image, build one design and export one PNG — no PDF. Use the
config's **Single-image size**; reference-copy mode keeps the reference page's
own size, so pick reference pages at that size. Other sizes are in
`reference/social_media_image_sizes.csv`; LinkedIn's landscape single image is
1200×627 and its square one 1200×1200.
