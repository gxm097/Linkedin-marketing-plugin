# Canva connector — what we know and what to verify

Canva's MCP server is documented tool-name by tool-name, but **not** schema by
schema. These four questions could not be answered from the docs and need
answering once against a real Canva account. The `canva-carousel` skill works
either way; the answers only let it take a shorter path.

Run through this with Canva connected (`/mcp` → `plugin:linkedin-marketing:canva`),
then record the answers here.

### 1. Can `create-design` make a custom-size design via MCP?
The REST API accepts `design_type: {type: "custom", width: 1080, height: 1080}`
(40–8000px per side, w×h ≤ 25,000,000). Whether the MCP tool exposes the same
field is unconfirmed.

- [ ] Answer:

### 2. Can one design hold all the slides?
`create-design` takes no page count or page list. Only *copy* operations accept
`page_numbers`, and those are a preview feature. If a design can hold N pages,
the skill can build one design instead of N.

- [ ] Answer:

### 3. What can `perform-editing-operations` actually do?
Undocumented. Needed: add a page, set a text element, place an image. Call the
`help` tool and inspect the schema.

- [ ] Answer:

### 4. Does a multi-page PDF export as one file or one URL per page?
The docs say "there is a download URL for each page in the design" for some
design types, and the PDF section doesn't say which. Export a 2-page design as
PDF and look at `job.urls`.

- [ ] Answer:

---

## Settled facts (no need to re-check)

- Endpoint is `https://api.canva.com/connect/v1/mcp`. Per-user OAuth; no service accounts.
- **Pro and above only:** `autofill-design`, `create-design-from-brand-template`, `list-brand-kits`, `search-brand-templates`, `resize-design`.
- **Works on Free:** `create-design`, `generate-design`, `export-design`, asset upload.
- PDF export fields: `type: "pdf"`, `export_quality` (`regular`|`pro`), `pages` (array; omit for all).
- Export is async — poll the job. **`job.urls` expire after 24 hours**, so download at once.
- `export-design` is limited to 20 requests/minute per user.
- `generate-design` is slow; allow 60 seconds.
- Autofill needs template fields tagged in the Canva editor: **Apps → Bulk Create → Labels**. Field names come from `get-brand-template-dataset`.
- Blank designs created via the API are deleted if not edited within 7 days.
