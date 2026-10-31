---
name: canva-carousel
description: Builds LinkedIn carousel slides in Canva from a slide script and exports them as images, then stitches them into the single multi-page PDF LinkedIn needs. Use when a carousel, slide deck, or multi-slide graphic is needed for a social post. Also handles single marketing images.
allowed-tools: Read, Write, Glob, Bash(uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/download.py" *), Bash(uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/build_pdf.py" *), mcp__canva__help, mcp__canva__list-brand-kits, mcp__canva__search-brand-templates, mcp__canva__get-brand-template-dataset, mcp__canva__autofill-design, mcp__canva__create-design-from-brand-template, mcp__canva__create-design, mcp__canva__generate-design, mcp__canva__generate-image, mcp__canva__upload-asset-from-url, mcp__canva__start-editing-transaction, mcp__canva__perform-editing-operations, mcp__canva__commit-editing-transaction, mcp__canva__get-design-pages, mcp__canva__get-export-formats, mcp__canva__merge-designs, mcp__canva__export-design
---

# Canva carousel builder

You turn a slide script into finished carousel slides in Canva, export them, and
produce one multi-page PDF.

**Why a PDF:** LinkedIn switched off native multi-image carousels in December
2023. A swipeable carousel is now a *document post* — one multi-page file, one
page per slide. Separate PNGs cannot be posted as a carousel.

## What you are given

- A **slide script**: 6–10 slides, each with a headline, optional sub-line, and image direction.
- An **output directory** (the post package folder).
- The **Image** section of `marketing-config.md`: style, brand colors, fonts, things to avoid.

## What you must produce

In the output directory:
- `slides/01.png`, `slides/02.png`, … — one image per slide, 1080×1080
- `carousel.pdf` — all slides, in order, one page each
- `slides/slides.json` — `{"mode": "...", "design_ids": [...], "slides": [{"n": 1, "headline": "...", "file": "01.png"}]}`

## Step 1 — Check what Canva can do for this user

If the Canva tools are not available at all, skip to **Degrading gracefully**.

Canva gates its best design tools by plan, so detect rather than assume:

1. Call `list-brand-kits`. If it succeeds, the user is on Canva Pro or above.
2. If it did, call `search-brand-templates` for a square (1080×1080) template.

Pick the mode:
- **brand-template** — a Brand Template was found (or `brand_template_id` is configured). Best output: genuinely on-brand, consistent slide to slide.
- **generate** — no Pro plan, no template found, or the config asks for it. Works on Canva Free.

Honour an explicit `canva_mode` of `brand-template` or `generate` over what you detected. If `brand-template` was asked for but no template exists, say so plainly and fall back to `generate` rather than failing.

Record the mode you used in `slides.json`.

**Canva is not bundled with the plugin.** It cannot be: `api.canva.com` offers
no dynamic client registration, and a client secret can only be supplied when a
server is added, not from a plugin's `.mcp.json`. So the user adds it themselves
with `claude mcp add`, naming it `canva`, and its tools are `mcp__canva__…`.
If none of those tools are available, Canva has not been connected — see
**Degrading gracefully** below.

**The tool input schemas are not published.** Call `help`, or read the error a
tool returns, rather than guessing argument names. If a call fails on its
arguments, inspect and retry — don't abandon the carousel.

## Step 2 — Build the slides

### brand-template mode
1. `get-brand-template-dataset` to learn the template's field names. These come from fields tagged in the Canva editor under **Apps → Bulk Create → Labels**; if the dataset is empty the template has not been tagged, so tell the user that and fall back to `generate` mode.
2. For each slide, `autofill-design` with that slide's text mapped onto the dataset fields.
3. Autofill is asynchronous — poll the returned job until it reports success.

### generate mode
1. `create-design` with a **custom** design type at `width: 1080, height: 1080`. Canva accepts custom sizes from 40–8000px, so this is within limits.
2. Place the slide's text and imagery. Use the editing transaction trio in order: `start-editing-transaction`, `perform-editing-operations`, `commit-editing-transaction`. Element ids come from the start call.
3. For imagery, `generate-image`, or `upload-asset-from-url` for an existing asset. Reference the returned asset id.
4. `generate-design` is an alternative for a whole slide from a prompt, but it is **slow** — allow up to 60 seconds and don't run many in parallel.

### Multi-page shortcut
If `NOTES-canva.md` records that a true multi-page design works, build one design with all slides and skip the per-slide loop — then `export-design` as PDF once and you are done after Step 3. Until that is confirmed, build one design per slide.

## Step 3 — Export and download

1. `export-design` each design as **PNG** at 1080×1080. (Confirm with `get-export-formats` if an export is refused.)
2. Exports are asynchronous: poll the job until `status` is `success`, then read `urls`.
3. **Download immediately** — Canva's export URLs expire after 24 hours. Pass every URL in **slide order**, in one call; the script numbers them `01.png`, `02.png`, … itself:
   ```bash
   uv run --locked --script "${CLAUDE_PLUGIN_ROOT}/scripts/download.py" <out>/slides "<url-1>" "<url-2>" ...
   ```
   Don't reach for `curl`: in Windows PowerShell 5.1 `curl` is an alias for `Invoke-WebRequest` and rejects `-fsSL`/`-o`. A 403 or 404 from this script means an export expired and has to be redone — it says so.
4. Respect the rate limit: `export-design` allows 20 requests per minute. For a 10-slide deck, pace the calls.
5. If an export fails with `license_required`, a premium Canva element is in the design. Tell the user which slide, and either swap the element or carry on without that slide's image.

## Step 4 — Stitch the PDF

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

## Step 5 — Check before returning

- One PNG per slide in the script, correctly numbered and in order
- `carousel.pdf` exists, opens, and has exactly as many pages as there are slides
- Slide 1 is the hook slide — the one that stops the scroll
- Text is legible at phone size: no more than ~15 words per slide, large type
- Brand colors and fonts from the config were applied
- Nothing from the config's **Avoid in images** list appears

## Degrading gracefully

Never abandon the week's post because Canva failed. If the connector is
unavailable, not authorised, or erroring:

1. Write `slides/slides.json` with the full slide script and the per-slide image prompts you would have used.
2. Create no `carousel.pdf`.
3. Report clearly: which step failed, the exact error, and that the post copy is still usable.
4. If it is an auth problem, say Canva needs connecting and point at the
   README's **Connect Canva** step. It takes a Canva app's own client ID and
   secret through `claude mcp add`, then `/mcp` → `canva` → sign in.
   Authorising `plugin:linkedin-marketing:canva` will not work: it fails with
   "does not support dynamic client registration".

The post copy ships either way. A missing graphic is a delay; a missing post is a missed week.

## Single images

For a single post image rather than a carousel, build one design and export one
PNG — no PDF. Sizes are in `reference/social_media_image_sizes.csv`; LinkedIn's
single post image is **1200×627**.
