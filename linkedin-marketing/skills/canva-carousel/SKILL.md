---
name: canva-carousel
description: Builds LinkedIn carousel slides in Canva from a slide script and exports them as images, then stitches them into the single multi-page PDF LinkedIn needs. Use when a carousel, slide deck, or multi-slide graphic is needed for a social post. Also handles single marketing images.
allowed-tools: Read, Write, Glob, Bash, mcp__plugin_linkedin-marketing_canva__help, mcp__plugin_linkedin-marketing_canva__list-brand-kits, mcp__plugin_linkedin-marketing_canva__search-brand-templates, mcp__plugin_linkedin-marketing_canva__get-brand-template-dataset, mcp__plugin_linkedin-marketing_canva__autofill-design, mcp__plugin_linkedin-marketing_canva__create-design-from-brand-template, mcp__plugin_linkedin-marketing_canva__create-design, mcp__plugin_linkedin-marketing_canva__generate-design, mcp__plugin_linkedin-marketing_canva__generate-image, mcp__plugin_linkedin-marketing_canva__upload-asset-from-url, mcp__plugin_linkedin-marketing_canva__start-editing-transaction, mcp__plugin_linkedin-marketing_canva__perform-editing-operations, mcp__plugin_linkedin-marketing_canva__commit-editing-transaction, mcp__plugin_linkedin-marketing_canva__get-design-pages, mcp__plugin_linkedin-marketing_canva__get-export-formats, mcp__plugin_linkedin-marketing_canva__merge-designs, mcp__plugin_linkedin-marketing_canva__export-design
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
3. **Download immediately** — Canva's export URLs expire after 24 hours. Save to `slides/NN.png`, numbered in slide order, zero-padded:
   ```bash
   curl -fsSL "<url>" -o slides/01.png
   ```
4. Respect the rate limit: `export-design` allows 20 requests per minute. For a 10-slide deck, pace the calls.
5. If an export fails with `license_required`, a premium Canva element is in the design. Tell the user which slide, and either swap the element or carry on without that slide's image.

## Step 4 — Stitch the PDF

```bash
python3 -I "${CLAUDE_PLUGIN_ROOT}/scripts/build_pdf.py" <out>/slides -o <out>/carousel.pdf
```

The script enforces LinkedIn's 300-page and 100 MB caps and warns if slide sizes
differ. If it reports a missing library, install Pillow and retry:
`python3 -m pip install Pillow`.

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
4. If it is an auth problem, tell the user to run `/mcp`, pick `plugin:linkedin-marketing:canva`, and sign in.

The post copy ships either way. A missing graphic is a delay; a missing post is a missed week.

## Single images

For a single post image rather than a carousel, build one design and export one
PNG — no PDF. Sizes are in `reference/social_media_image_sizes.csv`; LinkedIn's
single post image is **1200×627**.
