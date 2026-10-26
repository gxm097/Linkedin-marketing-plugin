---
description: Research the company and current trends, then build this week's LinkedIn carousel — slides in Canva, a ready-to-upload PDF, and the post copy
argument-hint: [topic or direction]
---

Create this week's LinkedIn carousel for the company defined in `marketing-config.md` (project root).

If I typed anything after the command, treat it as the topic or extra direction: $ARGUMENTS
If I typed nothing, choose the topic from the config's content pillars based on what's trending.

Follow these steps in order.

1. **Read the config.** Read `marketing-config.md` in the project root. If it's
   missing, stop and tell me to run `/linkedin-marketing:linkedin-setup` first. If the company name
   or website is blank, stop and tell me exactly which fields to fill in.

2. **Research.** Use the **marketing-researcher** agent. Pass it the config's
   company, audience, content pillars, and research settings. It returns a
   research brief.

3. **Let me choose the angle.** Show the brief's "Recommended angles" as 3 short
   lines, numbered, and **ask me which one to use.** Wait for my answer — do not
   pick one and carry on. If I say "you choose", take the strongest and tell me
   why in one line.

4. **Write it.** Pass the full brief and the chosen angle to the
   **carousel-writer** agent, along with the output directory
   `<Save posts to>/YYYY-MM-DD-<short-slug>/` (from the config; fallback
   `posts/`). It writes `post.md` and returns the slide script.

5. **Build the slides.** Invoke the **canva-carousel** skill with the slide
   script, the config's Image settings, and the same output directory. It builds
   the slides in Canva, exports them, and produces `carousel.pdf`.
   If Canva is unavailable, continue anyway — the post copy and slide script are
   still worth having. Say clearly that the graphic wasn't generated and why.

6. **Save the brief.** Write the research brief to `brief.md` in the same folder,
   so the sources behind the post stay with it.

7. **Show me the result.** The post copy in full, the slide headlines in order,
   the alternate hooks, and the folder path. Then ask whether I want changes
   before I upload it.

The finished folder should contain `post.md`, `carousel.pdf`, `slides/`, and
`brief.md`. The folder's date is what tells the weekly reminder that this week is
done, so don't rename it. The reminder only counts the week as shipped once
`carousel.pdf` is actually in there, so a run that stopped short will still be
flagged as due.
