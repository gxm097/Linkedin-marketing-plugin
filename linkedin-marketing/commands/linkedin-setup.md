---
description: Set up this project for LinkedIn marketing — write marketing-config.md and check the Canva connection
allowed-tools: Read, Write, Edit, Glob, Bash, WebFetch, mcp__plugin_linkedin-marketing_canva__list-brand-kits, mcp__plugin_linkedin-marketing_canva__search-brand-templates
---

Set up the LinkedIn marketing plugin for this project.

## 1. Don't clobber existing work

Check whether `marketing-config.md` already exists in the project root. If it
does, do **not** overwrite it. Tell me it exists and show which important fields
are still blank (company name, website, audience, content pillars), then offer to
fill just those in.

## 2. Start from what I typed at install

The install dialog already collected some of this. Read it so you don't ask me twice:

```bash
python3 -I -c "
import json, pathlib
for p in [pathlib.Path.home()/'.claude/settings.json']:
    try: d = json.loads(p.read_text())
    except Exception: continue
    for k, v in (d.get('pluginConfigs') or {}).items():
        if 'linkedin-marketing' in k: print(k, json.dumps(v, indent=2))
" 2>/dev/null || true
```

Use whatever that prints as the starting values. Anything it didn't give you, ask
me for: company name, website, and who our audience is. Then, if I say so, fetch
the website to suggest the industry, what we do, differentiators, voice, and 3
content pillars.

## 3. Check the Canva connection

Call `list-brand-kits`.

- **It worked** → the user is on Canva Pro or above. Call `search-brand-templates`
  for a square (1080×1080) template. If you find one, record its ID as the
  **Brand template ID** and set **Canva mode** to `brand-template`. Tell me which
  template you picked.
- **No square template** → set Canva mode to `brand-template` only if I say I'll
  make one; otherwise `generate`. Explain that a Brand Template gives much more
  consistent slides, and that its text fields must be tagged in Canva under
  **Apps → Bulk Create → Labels** before autofill can work.
- **It failed** → either Canva isn't connected or the plan is Free. Set Canva mode
  to `generate`, which works on Canva Free. If it looks like an auth problem, tell
  me to run `/mcp`, pick `plugin:linkedin-marketing:canva`, and sign in.

Either way, don't stop setup over Canva. `generate` mode works for everyone.

## 4. Write the config

Write `marketing-config.md` to the **project root** using exactly the template
below, filled in with what I gave you and what you found. Leave anything unknown
blank. It lives in my project, not in the plugin, so a plugin update never
overwrites it.

## 5. Tell me what's next

Show me the filled-in file, then tell me to run `/linkedin-marketing:weekly-carousel`
when I'm ready. Mention that I'll get a reminder here whenever the next one is due.

---

Template:

````markdown
# Marketing Config

Used by the marketing-researcher, carousel-writer, and linkedin-post-creator
agents and the /weekly-carousel command.
Fill in what you know; leave anything blank you don't. This file overrides
anything the agents find on the web, and anything set in the install dialog.

## Company
- **Name:** 
- **Website:** 
- **LinkedIn page:** 
- **Industry:** 
- **What we do (1–2 sentences):** 
- **Key products/services:** 
- **Differentiators:** 
- **Competitors (for context only, never mention by name):** 

## Audience
- **Who we're talking to:** (e.g., HR directors at mid-size companies)
- **Their pain points:** 
- **Audience time zone:** America/Chicago

## Voice
- **Tone:** (e.g., confident, friendly, practical, no hype)
- **Point of view:** (company "we" or personal "I")
- **Words/phrases to avoid:** synergy, game-changer, "excited to announce"
- **Emoji use:** none / light / moderate

## Content pillars
Topics we post about. When no topic is given, the agents pick from these based
on current trends.
1. 
2. 
3. 

## Post defaults
- **Platform:** LinkedIn
- **Goal:** engagement (awareness / engagement / leads / hiring)
- **Default call to action:** Ask a question to drive comments
- **Post length:** 150–250 words
- **Hashtags:** 3–5
- **Always-include hashtags:** 
- **Posts per week:** 1

## Carousel
LinkedIn carousels are document posts — one multi-page PDF, one page per slide.
- **Slides per carousel:** 7 (6–10)
- **Slide size:** 1080x1080
- **Canva mode:** auto (auto / brand-template / generate)
- **Brand template ID:** 
- **Slide headline max words:** 15

## Image
- **Image skill:** canva-carousel
- **Single-image size:** 1200x627
- **Style:** (e.g., clean modern illustration, flat colors)
- **Brand colors:** (e.g., #1A73E8, #FFFFFF, #202124)
- **Fonts / overlay text style:** 
- **Avoid in images:** real people's faces, fake logos, small text

## Research settings
- **Trend window:** last 30 days
- **Preferred sources:** (industry sites, publications you trust)
- **Sources to avoid:** 

## Output
- **Save posts to:** posts/
````
