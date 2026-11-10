---
description: Research current trends for the company in marketing-config.md, then create a single-image LinkedIn post
argument-hint: [topic or direction]
---

Create a **single-image** LinkedIn post for the company defined in
`marketing-config.md` (project root).

For the weekly carousel, use `/linkedin-marketing:weekly-carousel` instead. This
command is for the weeks when one image is enough.

If I typed anything after the command, treat it as the topic or extra direction: $ARGUMENTS
If I typed nothing, choose the topic from the config's content pillars based on what's trending.

Follow these steps in order:

1. Read `marketing-config.md` in the project root. If it's missing, stop and tell
   me to run `/linkedin-marketing:linkedin-setup` first. If the company name or website is blank,
   stop and tell me which fields to fill in. Then check `company-overview.md`:
   if it is missing or its status is not `approved`, stop and tell me to run
   `/linkedin-marketing:company-overview` — posts take their company facts from
   it.
2. Use the **marketing-researcher** agent to research the company and current
   trends. Pass it the config's company, audience, content pillars, and research
   settings.
3. Show me the brief's "Recommended angles" as 3 short lines, numbered, and
   **ask me which one to use.** Wait for my answer. If I say "you choose", take
   the strongest and tell me why in one line.
4. Pass the full research brief and the chosen angle to the
   **linkedin-post-creator** agent to write the post and the image spec (layout
   and on-image text) and save the package.
5. **Build the image here, in this conversation** — the agent cannot reach
   Canva. Invoke the **canva-carousel** skill with the image spec, the config's
   Image settings, and the post folder, and ask for a single image. If Canva is
   unavailable, carry on: the post copy is still worth having. Say clearly that
   the image wasn't built and why, and leave `post.md`'s image status as
   "awaiting build".
6. Show me the final post copy, the alternate hooks, the image previews and
   Canva link, and the folder path. **Ask me to approve the image** before it is
   saved in Canva and exported; nothing is committed or exported without that.
   If I ask for changes, make them and show the previews again. Once exported,
   set `post.md`'s image status to `image.png`.
7. Ask if I want any changes to the copy before I publish.
