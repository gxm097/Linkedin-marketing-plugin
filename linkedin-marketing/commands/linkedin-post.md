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
   stop and tell me which fields to fill in.
2. Use the **marketing-researcher** agent to research the company and current
   trends. Pass it the config's company, audience, content pillars, and research
   settings.
3. Show me the brief's "Recommended angles" as 3 short lines, numbered, and
   **ask me which one to use.** Wait for my answer. If I say "you choose", take
   the strongest and tell me why in one line.
4. Pass the full research brief and the chosen angle to the
   **linkedin-post-creator** agent to write the post, generate the image, and
   save the package.
5. When it's done, show me the final post copy, the alternate hooks, and the
   folder path. Ask if I want any changes before I publish.
