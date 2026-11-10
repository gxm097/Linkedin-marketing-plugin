---
description: Read the company website in depth and build company-overview.md — the approved source of every company fact in your posts. Run once before the first post, and again with "refresh" when the site changes.
argument-hint: [refresh]
---

Build or refresh the company overview for the company in `marketing-config.md`
(project root). Posts take every fact about the company from this file, so it
is worth ten minutes of my attention.

If I typed `refresh` after the command: $ARGUMENTS — rebuild into
`company-overview.draft.md` and leave the approved file alone until I approve
the new one.

1. **Read the config.** If `marketing-config.md` is missing, stop and tell me to
   run `/linkedin-marketing:linkedin-setup` first. If the company name or
   website is blank, stop and tell me which.

2. **Check what exists.**
   - No `company-overview.md` → build it.
   - `company-overview.md` with status `draft` → tell me, and ask whether to
     review that draft or rebuild it.
   - `company-overview.md` with status `approved` and no `refresh` → tell me
     when it was approved and ask whether I want a refresh. Don't rebuild
     without a yes.
   - `refresh` → build into `company-overview.draft.md`.

3. **Build.** Use the **company-profiler** agent. Tell it which file to write.
   It reads up to ~40 pages, so it takes a few minutes.

4. **Walk me through it.** Don't paste the whole file. Show, in order:
   - the one-paragraph overview
   - the product and service names, one line each
   - the story bank, numbered — these are what make posts specific
   - the proof points marked unverified, and the **Not to claim** list
   - the **Open questions** — ask me each one; my answers go into the file,
     marked `(from owner, <date>)`
   - on a refresh, the **Changes since the approved version**

   Then the file path, so I can read and edit the rest myself.

5. **Apply my edits.** Make the changes I ask for. When I say it's right — in
   words that approve it, not just "looks good" about one section — set the
   status line to `**Status:** approved <YYYY-MM-DD>` (on a refresh, replace
   `company-overview.md` with the draft and delete the draft). Never approve it
   on my behalf.

6. **Tell me what's next:** `/linkedin-marketing:linkedin-post` or
   `/linkedin-marketing:weekly-carousel`. Both refuse to run until the overview
   is approved.
